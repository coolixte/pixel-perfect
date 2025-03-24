import pygame
import os
import settings

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("Sélecteur d'images fluide avec zoom")

# Charger et redimensionner les images du dossier "imgs"
img_folder = "imgs"
image_files = [f for f in os.listdir(img_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Paramètres d'affichage
BASE_WIDTH = 500  # Taille normale des images
ZOOM_WIDTH = 700  # Taille zoomée au centre
SPACING = 50  # Espacement entre les images

images = []
original_sizes = []

for img_file in sorted(image_files):
    img = pygame.image.load(os.path.join(img_folder, img_file))

    # Calcul du ratio et redimensionnement à la taille de base
    ratio = BASE_WIDTH / img.get_width()
    new_height = int(img.get_height() * ratio)
    
    img = pygame.transform.scale(img, (BASE_WIDTH, new_height))
    images.append(img)
    original_sizes.append((BASE_WIDTH, new_height))  # Stocker la taille originale

# Position et animation
selected_index = 0
target_x = 0  # Position vers laquelle l'affichage doit glisser
current_x = 0  # Position actuelle pour l'effet fluide
zoom_factors = [1.0] * len(images)  # Facteur de zoom pour chaque image

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((30, 30, 30))  # Fond gris foncé

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Gestion des boutons fléchés
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if selected_index < len(images) - 1:
                    selected_index += 1
                    target_x -= (BASE_WIDTH + SPACING)  # Déplacer vers la droite
            if event.key == pygame.K_LEFT:
                if selected_index > 0:
                    selected_index -= 1
                    target_x += (BASE_WIDTH + SPACING)  # Déplacer vers la gauche

    # Animation fluide : interpolation pour glisser progressivement vers la cible
    current_x += (target_x - current_x) * 0.1  # Rend le mouvement progressif

    # Animation fluide : zoom progressif de l'image centrale
    for i in range(len(zoom_factors)):
        target_zoom = 1.4 if i == selected_index else 1.0  # Zoom max pour l'image centrale
        zoom_factors[i] += (target_zoom - zoom_factors[i]) * 0.1  # Lissage du zoom

    # Position de base du premier élément
    x = settings.SCREEN_WIDTH // 2 - BASE_WIDTH // 2 + current_x

    # Affichage des images avec zoom fluide
    for i, img in enumerate(images):
        img_width, img_height = original_sizes[i]

        # Appliquer le zoom progressif
        scale_factor = zoom_factors[i]
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        img_resized = pygame.transform.scale(img, (new_width, new_height))

        # Position Y pour centrer verticalement
        y = settings.SCREEN_HEIGHT // 2 - img_resized.get_height() // 2
        screen.blit(img_resized, (x, y))

        # Déplacer la position X pour la prochaine image
        x += BASE_WIDTH + SPACING

    # Dessiner les boutons fléchés
    arrow_color = (255, 255, 255)
    arrow_size = 60
    arrow_thickness = 5

    # Flèche gauche
    if selected_index > 0:
        pygame.draw.polygon(screen, arrow_color, [
            (50, settings.SCREEN_HEIGHT // 2), 
            (50 + arrow_size, settings.SCREEN_HEIGHT // 2 - arrow_size // 2), 
            (50 + arrow_size, settings.SCREEN_HEIGHT // 2 + arrow_size // 2)
        ], arrow_thickness)

    # Flèche droite
    if selected_index < len(images) - 1:
        pygame.draw.polygon(screen, arrow_color, [
            (settings.SCREEN_WIDTH - 50, settings.SCREEN_HEIGHT // 2), 
            (settings.SCREEN_WIDTH - 50 - arrow_size, settings.SCREEN_HEIGHT // 2 - arrow_size // 2), 
            (settings.SCREEN_WIDTH - 50 - arrow_size, settings.SCREEN_HEIGHT // 2 + arrow_size // 2)
        ], arrow_thickness)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
