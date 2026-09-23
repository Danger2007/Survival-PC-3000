import pygame
import settings


class NotesTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        self.is_nv = any(k in self.ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv'])

        self.font_main = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_header = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        self.font_footer = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)

        self.selected_index = 0
        self.desc_scroll_offset = 0
        self.focus_on_desc = False

        self.notes = [ # active shows what quests are active and what aren't, visible shows what quests are rendered and what aren't
            {
                "title": "Cargo Handler's Note",
                "active": True,
                "visible": True,
                "text": (
                    "Davis - You see the garbage in today's shipment? Even I can see that steel's no good- couple of beams were already rusted through. Someone's going to get killed.\n\n"
                    "Damn suits. Always trying to cut corners."
                )
            },
            {
                "title": "Holotape instructions",
                "active": True,
                "visible": True,
                "text": (
                    "This is a Holotape.\n\n"
                    "Holotapes are laser-readable media storage devices. In 2077, we used Holotapes to record audio and data files, like music, journals, even games. While this may seem primitive to you, two hundred years in the future, this was a common and popular technology in our time.\n\n"
                    "You can play holotapes with the Terminal on this table. Press the 'Load' button, insert the Holotape into the slot, and close it. It should play automatically."
                )
            },
            {
                "title": "Jamaica Plain flyer",
                "active": True,
                "visible": True,
                "text": (
                    "The Treasures of Jamaica Plain\n\n"
                    "October 17-23ndIn-game spelling, punctuation and/or grammar, 2077\n\n"
                    "8am-5pm Daily\n\n\n"
                    "Come and see the fabulous Treasures of Jamaica Plain! This stunning exhibit will be on display for one week only before these priceless items are sealed away, never to be seen again! Bring the entire family to this once-in-a-lifetime event!"
                )
            },
            {
                "title": "Signed, your neighbors",
                "active": True,
                "visible": True,
                "text": (
                    "Looking forward to seeing you.\n\n"
                    "Signed,\n"
                    "Your Neighbors"
                )
            }
            
#-------------------------------------------------------------------------
#                          Fallout New Vegas Notes
#-------------------------------------------------------------------------
        ] if not self.is_nv else [
            {
                "title": "Fine Dining",
                "active": True,
                "visible": True,
                "text": (
                    "These past few years, the very idea of \"fine dining\" has seemed beyond our grasp; indeed, where does one even begin to look for something artfully prepared and beautifully presented by a world-class chef? Well, fellow epicures, I have found the on place left on this Godforsaken earth with Real Food.\n\n"
                    "I present to you the Ultra-Luxe.\n\n"
                    "Ignore the rabble on the street, the petty farmers and everyman-types rubbing their pitiful few caps together in an attempt to elevate themselves to some semblance of class. Ignore the filthy, disease-ridden prostitutes of the Gomorrah, whoring themselves to anyone with coin. Walk briskly to the fabulous Ultra-Luxe, the only building in New Vegas worth your attention (you'll know it when you see it). Enter the doors of their restaurant, the Gourmand, and speak with the lovely Marjorie - she'll arrange for your care.\n\n"
                    "Dally not, for reservations must be made as early as possible. A sumptuous feast awaits you, dear friends."
                )
            },
            {
                "title": "Mayor Steyn's journal 1/2",
                "active": True,
                "visible": True,
                "text": (
                    "A promising development, if I do say so myself! It seems things went to hell at the NCR Correctional Facility north of here, and escaped prisoners are roaming free.\n\n"
                    "Sounds like a bad thing - and would be, if not for the political acumen and interpersonal alchemy of yours truly, Mayor Joseph B. Steyn, Esq. I sent the Jims out to make contact with the prisoners (or \"Powder Gangers,\" rather - they insist on this name) to let them know Nipton's open for trade - with free turns with the girls as door prizes.\n\n"
                    "Ha! You know they went for that deal. As sold by Little Jim, anyway. Big Jim, R.I.P.\n\n"
                    "I see a lot of potential here so long as I can keep the NCR troops and Powders (ridiculous name) from running into each other and shooting it out in the streets. Luckily, the troopers only come at night (double entendre), so if the Powders will only come during the day (again), I'll have them coming (third time, the charm) and going.\n\n"
                    "Yours in confidence,\n\n"
                    "Mayor Joseph B. Steyn, Esq."
                )
            },
            {
                "title": "Mayor Steyn's journal 2/2",
                "active": True,
                "visible": False,
                "text": (
                    "I can hardly believe my luck. Literally. I'm agape.\n\n"
                    "Just now I was approached by a rather intense young man calling himself \"Mr. Fox.\" (Yeah, right.) When we were alone in my office, he let it be known that he is a member of Caesar's Legion (!!!).\n\n"
                    "He knew that NCR troops and Powder Gangers often spend time in Nipton. It turns out that the Legion hates and wishes to make an example of both groups, the NCR for obvious reasons, and Powder Gangers for harassing Legion raiding parties on this side of the river.\n\n"
                    "I didn't have to think a moment about Mr. Fox's proposition before accepting it. All I have to do is convince the Powders to kidnap the NCR troops at night. When both groups are in town, the Legion boys will scoop everyone up. Ha!\n\n"
                    "For this simple task, I have been offered 8,000 CAPS!!! I could almost go back to the NCR right away... but who knows how much else I might make off this Legion lackey?\n\n"
                    "I'm going to start stockpiling some supplies in a safe house between here and the Mojave Outpost, just in case I decide to head back home in a hurry...\n\n"
                    "Very exciting!\n\n"
                    "Signed, with a steady hand,\n\n"
                    "(on the keyboard)\n\n"
                    "Super-Mayor Joseph B. Steyn, III Esq."
                )
            },
            {
                "title": "Mojave Express Delivery Order (6 of 6)",
                "active": False,
                "visible": True,
                "text": (
                    "INSTRUCTIONS\n\n"
                    "Deliver the package at the north entrance to the Vegas Strip, by way of Freeside. "
                    "An agent of the recipient will meet you at the checkpoint, take possession of the package, and pay for the delivery. "
                    "Bring the payment to Johnson Nash at the Mojave Express agency in Primm.\n\n"
                    "Bonus on completion: 250 caps.\n\n"
                    "MANIFEST\n\n"
                    "This package contains:\n\n"
                    "One (1) Oversized Poker Chip, composed of Platinum\n\n"
                    "CONTRACT PENALTIES\n\n"
                    "You are an authorized agent of the Mojave Express Package until delivery is complete and payment has been processed, "
                    "contractually obligated to complete this transaction and materially responsible for any malfeasance or loss. "
                    "Failure to deliver the proper recipient may result in forfeiture of your advance and bonus, criminal charges, and/or pursuit "
                    "by mercenary reclamation teams. The Mojave Express is not responsible for any injury or loss of life you experience as a result of said reclamation efforts."
                )
            }
        ]

        self._init_layout()

    def _get_ui_style(self):
        """Rileva lo stile dell'interfaccia da settings (default: 'Fallout_NV')."""
        return getattr(settings, "UI_STYLE", "Fallout_NV")

    def _get_sorted_visible_notes(self):
        """
        Restituisce le note visibili ordinate per lo stile NV (attive prima),
        o semplicemente le note visibili per lo stile Fallout 4.
        """
        visible = [note for note in self.notes if note.get("visible", True)]
        if self._get_ui_style() == "Fallout_NV":
            return sorted(visible, key=lambda n: 0 if n.get("active", True) else 1)
        return visible

    def _init_layout(self):
        left_w = int(self.draw_space.width * 0.42)
        right_w = self.draw_space.width - left_w - 30

        self.list_rect = pygame.Rect(
            self.draw_space.left + 12,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            left_w,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )

        self.details_rect = pygame.Rect(
            self.list_rect.right + 12,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            right_w,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )

    def handle_input(self, event):
        visible_notes = self._get_sorted_visible_notes()
        if not visible_notes:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_x, pygame.K_RIGHT, pygame.K_d) and not self.focus_on_desc:
                self.toggle_focus()
            elif event.key in (pygame.K_LEFT, pygame.K_a) and self.focus_on_desc:
                self.toggle_focus()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.select_item()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll(True)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll(False)

    def toggle_focus(self):
        """Alterna il focus tra la lista delle note e il testo del dettaglio a destra."""
        self.focus_on_desc = not self.focus_on_desc

    def select_item(self):
        # Le note non si equipaggiano/attivano manualmente dal player
        pass

    def scroll(self, direction: bool):
        visible_notes = self._get_sorted_visible_notes()
        if not visible_notes:
            return

        step = -1 if direction else 1

        if self.focus_on_desc:
            if 0 <= self.selected_index < len(visible_notes):
                lines = self._wrap_text(visible_notes[self.selected_index]["text"], self.font_main, self.details_rect.width - 25)
                max_visible = 8
                max_scroll = max(0, len(lines) - max_visible)
                self.desc_scroll_offset = max(0, min(max_scroll, self.desc_scroll_offset + step))
        else:
            self.desc_scroll_offset = 0
            self.selected_index = max(0, min(len(visible_notes) - 1, self.selected_index + step))

    def _wrap_text(self, text, font, max_width):
        """A capo automatico del testo che rispetta anche i ritorni a capo singoli e doppi (\\n)."""
        lines = []
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append("")
                continue

            words = paragraph.split(' ')
            line = ""
            for word in words:
                test_line = line + word + " "
                if font.size(test_line)[0] <= max_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line.strip())
                    line = word + " "
            if line:
                lines.append(line.strip())

        return lines

    def _draw_nv_scrollbar(self, x, top_y, bottom_y, total_items, visible_items, current_offset, color):
        """Disegna la scrollbar verticale (frecce e barra mobile, senza linea statica di sfondo)."""
        arrow_w = 2  # Larghezza totale freccia = 4px
        arrow_h = 4  # Altezza freccia
        notch = 1
        line_w = 1   # Spessore barra

        # Freccia Su
        up_arrow_pts = [
            (x, top_y),
            (x + arrow_w, top_y + arrow_h),
            (x, top_y + arrow_h - notch),
            (x - arrow_w, top_y + arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, up_arrow_pts)

        # Freccia Giù
        down_arrow_pts = [
            (x, bottom_y),
            (x + arrow_w, bottom_y - arrow_h),
            (x, bottom_y - arrow_h + notch),
            (x - arrow_w, bottom_y - arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, down_arrow_pts)

        track_top = top_y + arrow_h + 2
        track_bottom = bottom_y - arrow_h - 2
        track_length = track_bottom - track_top

        if track_length > 0 and total_items > 0:
            if total_items > visible_items:
                bar_length = max(8, int(track_length * (visible_items / total_items)))
                max_scroll = max(1, total_items - visible_items)
                scroll_ratio = min(1.0, max(0.0, current_offset / max_scroll))
                bar_top = track_top + int(scroll_ratio * (track_length - bar_length))
                bar_bottom = bar_top + bar_length
                pygame.draw.line(self.screen, color, (x, bar_top), (x, bar_bottom), line_w)
            else:
                pygame.draw.line(self.screen, color, (x, track_top), (x, track_bottom), line_w)

    def render(self):
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        color_middle = getattr(settings, "PIP_BOY_MIDDLE", (0, 191, 0))
        bg_dark = (0, 0, 0)

        visible_notes = self._get_sorted_visible_notes()
        if not visible_notes:
            return

        if self.selected_index >= len(visible_notes):
            self.selected_index = max(0, len(visible_notes) - 1)

        style = self._get_ui_style()

        if style == "Fallout_4":
            self._render_fo4_list(visible_notes, color_light, color_middle, bg_dark)
            if 0 <= self.selected_index < len(visible_notes):
                self._render_fo4_details(visible_notes[self.selected_index], color_light, color_middle)
        else:
            # Default: New Vegas
            self._render_nv_list(visible_notes, color_light, color_middle)
            if 0 <= self.selected_index < len(visible_notes):
                self._render_nv_details(visible_notes[self.selected_index], color_light, color_middle)

    # -------------------------------------------------------------------------
    # NEW VEGAS STYLE RENDERING
    # -------------------------------------------------------------------------

    def _render_nv_list(self, visible_notes, color_light, color_middle):
        y_cursor = self.list_rect.top
        text_offset_x = 8
        max_width = self.list_rect.width - text_offset_x - 3
        line_height = self.font_main.get_height() + 1
        padding = 2
        rendered_count = 0

        for i, note in enumerate(visible_notes):
            is_active = note.get("active", True)

            # Disegna la linea divisoria prima della prima nota inattiva
            if i > 0:
                prev_active = visible_notes[i - 1].get("active", True)
                if prev_active and not is_active:
                    line_y = y_cursor + 1
                    pygame.draw.line(
                        self.screen,
                        color_middle,
                        (self.list_rect.left + 2, line_y),
                        (self.list_rect.right - 2, line_y),
                        1
                    )
                    y_cursor += 4

            lines = self._wrap_text(note["title"], self.font_main, max_width)
            item_h = (len(lines) * line_height) + (padding * 2)

            if y_cursor + item_h > self.list_rect.bottom:
                break

            item_rect = pygame.Rect(self.list_rect.left, y_cursor, self.list_rect.width, item_h)

            if i == self.selected_index:
                border_color = color_light if not self.focus_on_desc else color_middle
                pygame.draw.rect(self.screen, border_color, item_rect, 1)

            text_color = color_light if is_active else color_middle

            text_y = y_cursor + padding
            for l in lines:
                txt_surf = self.font_main.render(l, True, text_color)
                self.screen.blit(txt_surf, (item_rect.left + text_offset_x, text_y))
                text_y += line_height

            y_cursor += item_h + 2
            rendered_count += 1

        # Scrollbar a SINISTRA dell'elenco delle note
        self._draw_nv_scrollbar(
            x=self.draw_space.left + 4,
            top_y=self.list_rect.top,
            bottom_y=self.list_rect.bottom - 5,
            total_items=len(visible_notes),
            visible_items=max(1, rendered_count),
            current_offset=self.selected_index,
            color=color_light
        )

    def _render_nv_details(self, note, color_light, color_middle):
        y_top = self.draw_space.top + 2
        right_x = self.draw_space.right - 10

        # Intestazioni in alto a destra
        act1 = self.font_main.render("Show Active Quest Notes X)", True, color_light)
        self.screen.blit(act1, (right_x - act1.get_width(), y_top + 1))

        act2 = self.font_main.render("Challenges Y)", True, color_light)
        self.screen.blit(act2, (right_x - act2.get_width(), y_top + 15))

        # Inizio area dettagli/istruzioni
        y_start = y_top + 48

        text_color = color_light if note.get("active", True) else color_middle

        lines = self._wrap_text(note["text"], self.font_main, self.details_rect.width - 15)
        line_height = self.font_main.get_height() + 3
        max_visible = 8
        visible_lines = lines[self.desc_scroll_offset : self.desc_scroll_offset + max_visible]

        current_y = y_start
        for l in visible_lines:
            if l:
                if l in ("INSTRUCTIONS", "MANIFEST", "CONTRACT PENALTIES"):
                    surf = self.font_header.render(l, True, text_color)
                else:
                    surf = self.font_main.render(l, True, text_color)
                self.screen.blit(surf, (self.details_rect.left, current_y))
            current_y += line_height

        box_h = (self.details_rect.bottom - y_start) + 2
        if self.focus_on_desc:
            desc_box = pygame.Rect(self.details_rect.left - 4, y_start - 4, self.details_rect.width - 10, box_h)
            pygame.draw.rect(self.screen, color_light, desc_box, 1)

        # Scrollbar a DESTRA del riquadro dei dettagli
        self._draw_nv_scrollbar(
            x=self.details_rect.right - 8,
            top_y=y_start - 4,
            bottom_y=self.details_rect.bottom - 5,
            total_items=len(lines),
            visible_items=max_visible,
            current_offset=self.desc_scroll_offset,
            color=color_light
        )

    # -------------------------------------------------------------------------
    # FALLOUT 4 STYLE RENDERING
    # -------------------------------------------------------------------------

    def _render_fo4_list(self, visible_notes, color_light, color_middle, bg_dark):
        y_cursor = self.list_rect.top
        text_offset_x = 8
        line_height = self.font_main.get_height() + 1
        padding = 2
        rendered_count = 0

        for i, note in enumerate(visible_notes):
            lines = self._wrap_text(note["title"], self.font_main, self.list_rect.width - text_offset_x - 3)
            item_h = (len(lines) * line_height) + (padding * 2)

            if y_cursor + item_h > self.list_rect.bottom - 5:
                break

            item_rect = pygame.Rect(self.list_rect.left + text_offset_x - 3, y_cursor, self.list_rect.width - text_offset_x + 3, item_h)

            if i == self.selected_index:
                highlight_surf = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
                alpha = 200 if not self.focus_on_desc else 100
                highlight_surf.fill((*color_light[:3], alpha))
                self.screen.blit(highlight_surf, item_rect.topleft)
                text_color = bg_dark if not self.focus_on_desc else color_light
            else:
                text_color = color_light if note.get("active", True) else color_middle

            text_y = y_cursor + padding
            for l in lines:
                txt_surf = self.font_main.render(l, True, text_color)
                self.screen.blit(txt_surf, (item_rect.left + 3, text_y))
                text_y += line_height

            y_cursor += item_h + 1
            rendered_count += 1

        # Scrollbar a SINISTRA dell'elenco delle note (stile Fallout 4)
        self._draw_nv_scrollbar(
            x=self.draw_space.left + 4,
            top_y=self.list_rect.top,
            bottom_y=self.list_rect.bottom - 5,
            total_items=len(visible_notes),
            visible_items=max(1, rendered_count),
            current_offset=self.selected_index,
            color=color_light
        )

    def _render_fo4_details(self, note, color_light, color_middle):
        y_start = self.details_rect.top
        text_color = color_light if note.get("active", True) else color_middle

        lines = self._wrap_text(note["text"], self.font_main, self.details_rect.width - 15)
        line_height = self.font_main.get_height() + 3
        max_visible = 9
        visible_lines = lines[self.desc_scroll_offset : self.desc_scroll_offset + max_visible]

        current_y = y_start
        for l in visible_lines:
            if l:
                surf = self.font_main.render(l, True, text_color)
                self.screen.blit(surf, (self.details_rect.left, current_y))
            current_y += line_height

        # Scrollbar a DESTRA del riquadro dei dettagli (stile Fallout 4)
        if len(lines) > max_visible:
            self._draw_nv_scrollbar(
                x=self.details_rect.right - 8,
                top_y=y_start,
                bottom_y=self.details_rect.bottom - 5,
                total_items=len(lines),
                visible_items=max_visible,
                current_offset=self.desc_scroll_offset,
                color=color_light
            )