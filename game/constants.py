from .load_images import load_smoke_images, load_electric_images, load_csmoke_images, load_gas_images, load_physic_images

## constants.py
BOTTOM_Y = 490
smoke_images = load_smoke_images()
electric_images = load_electric_images()
gas_images = load_gas_images()
physic_images = load_physic_images()
csmoke_images1, csmoke_images2 = load_csmoke_images()