## Scripts de apoyo

Autor: Jonathan Chávez

`geo_to_mask.py` convierte la geometría de .npz a una máscara en donde cada id de PMT es un pixel, para después hacer el mapeo de los valores a imagen.

`npz_to_images.py` convierte simulaciones en .npz a imagenes (matrices numpy) usando una máscara de geometría.

Las instrucciones son simples:

1. Descargue su archivo de geometría .npz y genere una simulación .npz.
2. Convierta la geometría a .npy usando `geo_to_mask.npy`.
3. Convierta su simulación .npz con `npz_to_images.npy` usando la geometría anterior.

Para su ayuda, ya hay una geometría de ejemplo en `/geoms` y una simulación en `/simulations`.



El código no está muy bien organizado, pero funciona.


Referencias:

[Convertidor de eventos npz a imagen - Notebook](https://colab.research.google.com/drive/1cKxkxsR-ZRYvvxEeAHwK9C1UO1Gi7vuZ?usp=sharing)
