from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from constants import MEAL_SLOTS
from db import (
    init_db, list_recipes, upsert_recipe, delete_recipe,
    get_recipe_by_title, list_plan, set_plan, get_conn
)
from pdf_export import build_mealprep_pdf
import re

def parse_ing(line):
    line = line.strip().lstrip("• ").strip()
    if not line:
        return None
    core = re.sub(r"\(.*?\)", "", line).strip()
    m = re.match(r"^(\d+(?:[\.,]\d+)?)[\s]*([a-zA-Z%µ]+)?\s+(.*)$", core)
    if m:
        return float(m.group(1).replace(",", ".")), (m.group(2) or ""), m.group(3).strip()
    m2 = re.match(r"^(\d+)\s+(.*)$", core)
    if m2:
        return float(m2.group(1)), "", m2.group(2).strip()
    return None, "", line

class MealApp(MDApp):
    meal_slots = MEAL_SLOTS
    recipe_titles = ["Seleziona ricetta"]

    def build(self):
        # Tema
        self.theme_cls.theme_style = "Light"  # "Dark" per scuro
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "Pink"

        init_db()
        ui = Builder.load_file("ui.kv")
        Clock.schedule_once(lambda *_: self.refresh_recipe_titles(), 0.05)
        Clock.schedule_once(lambda *_: self.refresh_recipes_list(), 0.1)
        Clock.schedule_once(lambda *_: self.refresh_plan_view(week=1), 0.2)
        return ui

    def switch_tab(self, tab_name):
        self.root.ids.tabs.switch_tab(tab_name)

    # ---------- Ricette ----------
    def refresh_recipe_titles(self):
        self.recipe_titles = ["Seleziona ricetta"] + [r["title"] for r in list_recipes()]
        # aggiorna potenziali dropdown/spinner nel planner se sostituiti in futuro

    def refresh_recipes_list(self):
        rows = list_recipes()
        data = []
        for r in rows:
            data.append({
                "text": f"{r['title']}  ({r['meal_slot'] or '-'})",
                "on_release": lambda x=r: self.load_recipe_into_form(x)
            })
        self.root.ids.recipes_rv.clear_widgets()
        from kivymd.uix.list import OneLineListItem
        for item in data:
            self.root.ids.recipes_rv.add_widget(
                OneLineListItem(text=item["text"], on_release=item["on_release"])
            )

    def load_recipe_into_form(self, r):
        ids = self.root.ids
        ids.rcp_title.text = r["title"]
        ids.rcp_slot.text = r["meal_slot"] or self.meal_slots[0]
        ids.rcp_ing.text = r["ingredients"] or ""
        ids.rcp_steps.text = r["steps"] or ""
        ids.rcp_kcal.text = str(r["kcal"] or "")
        ids.rcp_p.text = str(r["protein"] or "")
        ids.rcp_c.text = str(r["carbs"] or "")
        ids.rcp_f.text = str(r["fat"] or "")
        ids.rcp_link.text = r["ref_link"] or ""

    def save_recipe(self):
        ids = self.root.ids
        title = ids.rcp_title.text.strip()
        if not title:
            return
        current = get_recipe_by_title(title)
        data = {
            "id": current["id"] if current else None,
            "title": title,
            "meal_slot": ids.rcp_slot.text if ids.rcp_slot.text in MEAL_SLOTS else None,
            "ingredients": ids.rcp_ing.text.strip(),
            "steps": ids.rcp_steps.text.strip(),
            "kcal": float(ids.rcp_kcal.text) if ids.rcp_kcal.text else 0.0,
            "protein": float(ids.rcp_p.text) if ids.rcp_p.text else 0.0,
            "carbs": float(ids.rcp_c.text) if ids.rcp_c.text else 0.0,
            "fat": float(ids.rcp_f.text) if ids.rcp_f.text else 0.0,
            "ref_link": ids.rcp_link.text.strip()
        }
        upsert_recipe(data)
        self.refresh_recipe_titles()
        self.refresh_recipes_list()
        ids.snackbar_text.text = "Ricetta salvata ✅"
        ids.snackbar.open()

    def delete_selected_recipe(self):
        ids = self.root.ids
        title = ids.rcp_title.text.strip()
        if not title:
            return
        r = get_recipe_by_title(title)
        if r:
            delete_recipe(r["id"])
            for fid in ("rcp_title","rcp_ing","rcp_steps","rcp_kcal","rcp_p","rcp_c","rcp_f","rcp_link"):
                ids[fid].text = ""
            self.refresh_recipe_titles()
            self.refresh_recipes_list()
            ids.snackbar_text.text = "Ricetta eliminata 🗑️"
            ids.snackbar.open()

    # ---------- Planner ----------
    def _week_from_spinner(self, s): return int(s.split()[-1])
    def _day_from_spinner(self, s): return int(s.split()[-1])

    def save_plan(self, slot, recipe_title, portions_text):
        ids = self.root.ids
        w = self._week_from_spinner(ids.pl_week.text)
        d = self._day_from_spinner(ids.pl_day.text)
        r = get_recipe_by_title(recipe_title) if recipe_title and recipe_title != "Seleziona ricetta" else None
        portions = float(portions_text) if portions_text else 1.0
        set_plan(w, d, slot, r["id"] if r else None, portions)
        self.refresh_plan_view(w)
        ids.snackbar_text.text = "Planner aggiornato ✅"
        ids.snackbar.open()

    def refresh_plan_view(self, week):
        rows = list_plan(week)
        self.root.ids.plan_rv.clear_widgets()
        from kivymd.uix.list import OneLineListItem
        for r in rows:
            self.root.ids.plan_rv.add_widget(
                OneLineListItem(text=f"G{r['day']} – {r['slot']}: {r['title'] or '-'} x{r['portions']}")
            )

    # ---------- Spesa ----------
    def calc_shopping(self):
        ids = self.root.ids
        w = self._week_from_spinner(ids.shop_week.text)
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""SELECT p.portions, r.ingredients
                       FROM plan p JOIN recipes r ON p.recipe_id=r.id
                       WHERE p.week=?""",(w,))
        rows = cur.fetchall(); conn.close()
        items = {}
        for r in rows:
            pf = float(r["portions"] or 1.0)
            for line in (r["ingredients"] or "").splitlines():
                qty, unit, name = parse_ing(line)
                key = (name.lower(), unit)
                if key not in items:
                    items[key] = {"name": name, "unit": unit, "qty": 0.0, "unknown": False}
                if qty is None:
                    items[key]["unknown"] = True
                else:
                    items[key]["qty"] += qty * pf
        self.root.ids.shop_rv.clear_widgets()
        from kivymd.uix.list import OneLineListItem
        for (_, unit), v in sorted(items.items(), key=lambda kv: kv[1]["name"].lower()):
            qtxt = "q.b." if v["unknown"] else f"{round(v['qty'],2)} {unit or ''}"
            self.root.ids.shop_rv.add_widget(OneLineListItem(text=f"- {v['name']}: {qtxt}"))

    # ---------- Export ----------
    def do_export_pdf(self):
        ids = self.root.ids
        w = self._week_from_spinner(ids.exp_week.text)
        fname = f"MealPrep_Settimana{w}.pdf"
        build_mealprep_pdf(fname, w)
        ids.exp_status.text = f"Creato: {fname} (cartella app). Condividilo o aprilo con un file manager."
        ids.snackbar_text.text = "PDF generato 🖨️"
        ids.snackbar.open()

if __name__ == "__main__":
    MealApp().run()
