import os
import pygame
import settings

_SKILL_ICON_CACHE = {}

def find_image_file(skill_name):
    """Cerca il file immagine gestendo sia PascalCase che casi speciali e percorsi assoluti."""
    clean_name = skill_name.strip()
    
    name_map = {
        "big guns": "Guns",
        "small guns": "Guns",
        "energy weapons": "EnergyWeapons",
        "melee weapons": "MeleeWeapons",
    }
    
    key_lower = clean_name.lower()
    if key_lower in name_map:
        target_name = name_map[key_lower]
    else:
        target_name = "".join(word.capitalize() for word in clean_name.split())

    possible_filenames = [
        f"{target_name}.webp",
        f"{target_name}.png",
        f"{target_name}.dds",
        f"{clean_name.lower().replace(' ', '_')}.webp"
    ]
    
    base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [
        os.path.join(base_dir, "images", "new_vegas_icons", "skills_nv"),
        os.path.join(base_dir, "images", "skills"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "new_vegas_icons", "skills_nv")
    ]
    
    for s_dir in search_dirs:
        for fname in possible_filenames:
            full_path = os.path.normpath(os.path.join(s_dir, fname))
            if os.path.exists(full_path):
                return full_path
                
    print(f"[DEBUG PIP-BOY] Immagine NON trovata per '{skill_name}' (cercato {target_name}.webp)")
    return None


def load_skill_icon(skill_name):
    """Carica l'immagine dalla cache o dal disco con fallback PIL per webp/dds."""
    if skill_name in _SKILL_ICON_CACHE:
        return _SKILL_ICON_CACHE[skill_name]
        
    file_path = find_image_file(skill_name)
    if not file_path:
        _SKILL_ICON_CACHE[skill_name] = None
        return None
    
    try:
        img = pygame.image.load(file_path).convert_alpha()
        _SKILL_ICON_CACHE[skill_name] = img
        return img
    
    except Exception as e_pygame:
        try:
            from PIL import Image
            pil_img = Image.open(file_path).convert("RGBA")
            data = pil_img.tobytes()
            img = pygame.image.fromstring(data, pil_img.size, "RGBA").convert_alpha()
            _SKILL_ICON_CACHE[skill_name] = img
            return img
        except Exception as e_pil:
            print(f"[DEBUG PIP-BOY] Errore decodifica immagine {file_path}: {e_pil}")
    
    _SKILL_ICON_CACHE[skill_name] = None
    return None


def colorize_surface(surface, color):
    """Applica la tinta del Pip-Boy a un'icona bianca conservandone l'alpha."""
    if surface is None:
        return None
    
    tinted = surface.copy()
    
    r, g, b = color[0], color[1], color[2]
    tinted.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    
    return tinted


def render_multiline_text(screen, text, font, color, rect):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= rect.width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
        
    y = rect.top
    line_spacing = font.get_height() + 3
    for line in lines:
        if y + font.get_height() > rect.bottom:
            break
        txt_surface = font.render(line, True, color)
        screen.blit(txt_surface, (rect.left, y))
        y += line_spacing


def draw_skills_tab(screen, skills_data, selected_index, color, base_font, screen_w, screen_h):
    if not skills_data:
        return

    # 1. LIST FONT / LINE HEIGHT
    FONT_SIZE = 12
    skill_font = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE)
    LINE_HEIGHT = 18

    # Layout
    left_x = int(screen_w * 0.12)
    left_w = int(screen_w * 0.36)
    
    right_x = int(screen_w * 0.52)
    right_w = int(screen_w * 0.45)
    
    top_y = int(screen_h * 0.18)
    bottom_y = int(screen_h * 0.82)
    available_h = bottom_y - top_y

    # 2. SCROLL
    MAX_VISIBLE_ITEMS = max(1, available_h // LINE_HEIGHT)
    scroll_offset = max(0, min(selected_index - MAX_VISIBLE_ITEMS // 2, len(skills_data) - MAX_VISIBLE_ITEMS))
    scroll_offset = max(0, scroll_offset)

    # 3. ARROWS / SLIDER
    slider_x = left_x - 18
    arrow_w = 5
    arrow_h = 8
    notch = 3

    # ARROW UP
    top_arrow_y = top_y
    up_arrow_pts = [
        (slider_x, top_arrow_y),
        (slider_x + arrow_w, top_arrow_y + arrow_h),
        (slider_x, top_arrow_y + arrow_h - notch),
        (slider_x - arrow_w, top_arrow_y + arrow_h)
    ]
    pygame.draw.polygon(screen, color, up_arrow_pts)

    # ARROW DOWN
    bottom_arrow_y = bottom_y
    down_arrow_pts = [
        (slider_x, bottom_arrow_y),
        (slider_x + arrow_w, bottom_arrow_y - arrow_h),
        (slider_x, bottom_arrow_y - arrow_h + notch),
        (slider_x - arrow_w, bottom_arrow_y - arrow_h)
    ]
    pygame.draw.polygon(screen, color, down_arrow_pts)

    # SLIDER
    track_top = top_arrow_y + arrow_h - notch + 5
    track_bottom = bottom_arrow_y - arrow_h + notch - 5
    track_length = track_bottom - track_top

    total_items = len(skills_data)
    if total_items > MAX_VISIBLE_ITEMS:
        bar_length = max(12, int(track_length * (MAX_VISIBLE_ITEMS / total_items)))
        max_scroll = total_items - MAX_VISIBLE_ITEMS
        scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
        
        bar_top = track_top + int(scroll_ratio * (track_length - bar_length))
        bar_bottom = bar_top + bar_length
        pygame.draw.line(screen, color, (slider_x, bar_top), (slider_x, bar_bottom), 2)

    # 4. SKILLS LIST
    visible_skills = skills_data[scroll_offset : scroll_offset + MAX_VISIBLE_ITEMS]
    
    for idx_in_view, skill in enumerate(visible_skills):
        actual_index = scroll_offset + idx_in_view
        y_pos = top_y + (idx_in_view * LINE_HEIGHT)
        
        is_selected = (actual_index == selected_index)
        
        if is_selected:
            select_rect = pygame.Rect(left_x - 4, y_pos, left_w + 8, LINE_HEIGHT - 1)
            pygame.draw.rect(screen, color, select_rect, 1)
            
        # Name Skill
        name_surf = skill_font.render(skill["name"], True, color)
        screen.blit(name_surf, (left_x, y_pos + (LINE_HEIGHT - name_surf.get_height()) // 2))
        
        # Value + Modifier
        val_str = str(skill.get("value", 0))
        if skill.get("mod"):
            val_str += f" ({skill['mod']})"
            
        val_surf = skill_font.render(val_str, True, color)
        val_x = left_x + left_w - val_surf.get_width()
        screen.blit(val_surf, (val_x, y_pos + (LINE_HEIGHT - val_surf.get_height()) // 2))

    # 5. RIGHT COLUMN: SKILL ICON + DESCRIPTION
    if 0 <= selected_index < len(skills_data):
        selected_skill = skills_data[selected_index]
        
        img_h = int(available_h * 0.60)
        img_rect = pygame.Rect(right_x, top_y, right_w, img_h)
        
        icon_surface = load_skill_icon(selected_skill["name"])
        if icon_surface:
            orig_w, orig_h = icon_surface.get_size()
            scale = min(img_rect.width / orig_w, img_rect.height / orig_h)
            new_size = (int(orig_w * scale), int(orig_h * scale))
            
            # Scalatura uniforme
            scaled_img = pygame.transform.smoothscale(icon_surface, new_size)
            
            # Ricolorazione dinamica in base al colore del Pip-Boy
            colored_img = colorize_surface(scaled_img, color)
            
            center_x = right_x + (right_w - new_size[0]) // 2
            center_y = top_y + (img_h - new_size[1]) // 2
            screen.blit(colored_img, (center_x, center_y))

        # ICON-DESCRIPTION DIVIDER
        divider_y = top_y + img_h + 5
        pygame.draw.line(screen, color, (right_x, divider_y), (right_x + right_w, divider_y), 1)
        pygame.draw.line(screen, color, (right_x + right_w, divider_y), (right_x + right_w, divider_y + 7), 1)
        
        # DESCRIPTION
        desc_y = divider_y + 5
        skill_font2 = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE - 3)
        desc_rect = pygame.Rect(right_x, desc_y, right_w - 5, bottom_y + 10)
        render_multiline_text(screen, selected_skill.get("desc", ""), skill_font2, color, desc_rect)