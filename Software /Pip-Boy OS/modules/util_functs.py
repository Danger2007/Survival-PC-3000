import datetime
import pygame
import settings
import os
import xml.etree.ElementTree as ET
import re

class Utils:
         
    @staticmethod
    def tint_image(image, color=settings.PIP_BOY_LIGHT):
        """Tint image with specified color while preserving alpha"""
        tinted = image.copy()
        # Multiply RGB channels with color, preserve original alpha
        tinted.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGB_MULT)
        return tinted       
    
    @staticmethod
    def scale_image(image, scale: float):
        return pygame.transform.smoothscale_by(image, scale)
        
    @staticmethod
    def scale_image_abs(image, width: float = None, height: float = None):
        """
        Scale image absolutely but keep aspect ratio.
        """
        if width is None and height is None:
            return image
        
        if width is None:
            width = image.get_width() * (height / image.get_height())
        elif height is None:
            height = image.get_height() * (width / image.get_width())
        
        # Ensure width and height are integers
        return pygame.transform.smoothscale(
            image, 
            (int(width), int(height))
        )
    
    @staticmethod
    def load_images(folder: str, tint=settings.PIP_BOY_LIGHT):
        """
        Load and tint all PNG images in the specified folder.
        """
        try:
            images = [
                Utils.tint_image(
                    pygame.image.load(os.path.join(folder, f)).convert_alpha(),
                    tint
                ) for f in sorted(os.listdir(folder)) if f.endswith(".png")
            ]
            return images
        except FileNotFoundError:
            return []

    @staticmethod        
    def load_svgs_dict(folder: str, scale: int, tint=settings.PIP_BOY_LIGHT):
        """
        Load and tint all SVG images in the specified folder.
        """
        try:
            images = {
                f: Utils.tint_image(
                    pygame.image.load_sized_svg(os.path.join(folder, f), (scale, scale)).convert_alpha(),
                    tint
                ) for f in sorted(os.listdir(folder)) if f.endswith(".svg")
            }
            images= {k.replace(".svg", ""): v for k, v in images.items()}
            return images
        except FileNotFoundError:
            return {}
        
        
        
    @staticmethod
    def load_svgs(folder: str, scale: float, tint=settings.PIP_BOY_LIGHT, load_transforms=False):
        """
        Load, scale, and tint all SVG images in the specified folder.
        - Maintains aspect ratio using the first SVG's width as the reference.
        - Normalizes transforms (tx, ty) to be relative to the first SVG's position.
        - Scales transforms uniformly to match the target size.
        """
        try:
            svg_files = [f for f in sorted(os.listdir(folder)) if f.endswith(".svg")]
            if not svg_files:
                return []
            
            # Parse first SVG to get reference dimensions
            first_svg_path = os.path.join(folder, svg_files[0])
            first_width, first_height = Utils._get_svg_dimensions(first_svg_path)
            if load_transforms:
                first_tx, first_ty = Utils._get_svg_transform(first_svg_path)
            
            if first_width <= 0 or first_height <= 0:
                # Fallback to avoid division by zero
                scale_factor = 1.0
            else:
                # Uniform scaling based on first SVG's width to preserve aspect ratio
                scale_factor = scale / first_width
            
            images = []
            transforms = []
            for f in svg_files:
                svg_path = os.path.join(folder, f)
                width, height = Utils._get_svg_dimensions(svg_path)
                
                # Calculate target size while preserving aspect ratio
                target_width = int(width * scale_factor)
                target_height = int(height * scale_factor)
                target_size = (target_width, target_height)
                
                if load_transforms:
                    tx, ty = Utils._get_svg_transform(svg_path)
                    # Calculate deltas relative to first SVG's transform
                    delta_tx = tx - first_tx
                    delta_ty = ty - first_ty
                    # Scale transforms using the uniform factor
                    scaled_tx = delta_tx * scale_factor
                    scaled_ty = delta_ty * scale_factor
                    transforms.append((scaled_tx, scaled_ty))
                
                # Load and scale the SVG
                img = pygame.image.load_sized_svg(svg_path, target_size).convert_alpha()
                tinted_img = Utils.tint_image(img, tint)
                images.append(tinted_img)
            
            return (images, transforms) if load_transforms else images
        except FileNotFoundError:
            return []
    
    
    @staticmethod
    def _get_svg_dimensions(svg_path):
        """Parse width/height from viewBox (preferred) or width/height attributes."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            viewbox = root.get('viewBox')
            if viewbox:
                parts = viewbox.strip().split()
                if len(parts) >= 4:
                    vb_width = parts[2]
                    vb_height = parts[3]
                    # Clean non-numeric characters
                    vb_width = re.sub(r'[^\d.]', '', vb_width) if vb_width else '0'
                    vb_height = re.sub(r'[^\d.]', '', vb_height) if vb_height else '0'
                    return float(vb_width), float(vb_height)
            # Fallback to width/height attributes
            width = root.get('width', '0')
            height = root.get('height', '0')
            width = re.sub(r'[^\d.]', '', width)
            height = re.sub(r'[^\d.]', '', height)
            return float(width or 0), float(height or 0)
        except:
            return 0.0, 0.0
    
    @staticmethod
    def _get_svg_transform(svg_path):
        """Parse the transform tx and ty from an SVG file."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            tx, ty = 0.0, 0.0
            # Check root element's transform first
            transform_str = root.get('transform', '')
            if transform_str:
                tx, ty = Utils._parse_transform(transform_str)
            # Search children if root has no transform
            if tx == 0 and ty == 0:
                for elem in root.iter():
                    if elem == root:
                        continue  # Skip root
                    transform_str = elem.get('transform', '')
                    if transform_str:
                        elem_tx, elem_ty = Utils._parse_transform(transform_str)
                        if elem_tx != 0 or elem_ty != 0:
                            tx, ty = elem_tx, elem_ty
                            break
            return tx, ty
        except:
            return 0.0, 0.0
    
    @staticmethod
    def _parse_transform(transform_str):
        """Extract tx and ty from a transform string."""
        if not transform_str:
            return (0.0, 0.0)
        # Check for translate
        translate_match = re.match(r'translate\(\s*([-\d.]+)(?:\s*,\s*|\s+)([-\d.]+)\s*\)', transform_str)
        if translate_match:
            tx = float(translate_match.group(1))
            ty = float(translate_match.group(2))
            return (tx, ty)
        # Check for matrix
        matrix_match = re.match(r'matrix\(\s*([-\d.]+)[,\s]+([-\d.]+)[,\s]+([-\d.]+)[,\s]+([-\d.]+)[,\s]+([-\d.]+)[,\s]+([-\d.]+)\s*\)', transform_str)
        if matrix_match:
            tx = float(matrix_match.group(5))
            ty = float(matrix_match.group(6))
            return (tx, ty)
        return (0.0, 0.0)
        
    
    @staticmethod
    def load_svg(scale: int, path: str, tint=settings.PIP_BOY_LIGHT):
        """
        Load an SVG file, scale it, and apply a tint.
        """
        if path.endswith(".svg"):
            width, height = Utils._get_svg_dimensions(path)
            scale_factor = scale / width

            # Calculate target size while preserving aspect ratio
            target_width = int(width * scale_factor)
            target_height = int(height * scale_factor)
            target_size = (target_width, target_height)
            # Assuming pygame.image.load_sized_svg exists
            return Utils.tint_image(
                pygame.image.load_sized_svg(path, target_size).convert_alpha(),
                tint
            )



    
    @staticmethod
    def play_sfx(sound_file, volume=settings.VOLUME, start=0, channel=None):
        """
        Play a sound file.
        """
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            if channel is None:
                sound.play(start)
            else:
                # Get the channel object once and reuse it
                ch = pygame.mixer.Channel(channel)
                ch.stop()  # Stops any sound currently on this channel
                ch.play(sound)
                
    @staticmethod
    def lerp(start, end, start_range, end_range, value):
        """
        Linear interpolation between two values.
        """
        return start + (end - start) * ((value - start_range) / (end_range - start_range))
    
    
    @staticmethod
    def get_date():
        now = datetime.datetime.now()
        current_date = f"{now.day}.{now.month}"
        current_year = str(int(now.strftime("%Y")) + settings.YEARS_ADDED)
        date = f"{current_date}.{current_year}"
        return date


    @staticmethod
    def get_time():
        now = datetime.datetime.now()    
        current_time = now.strftime("%I:%M%p")
        return current_time
    
    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if a file exists at the given path."""
        return os.path.isfile(path)
