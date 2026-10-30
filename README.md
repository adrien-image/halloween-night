# Halloween — une soirée presque parfaite ?

Histoire interactive dont vous êtes le héros, publiée sur GitHub Pages.

- `story/Halloween_version_2.md` : le texte source de l'histoire.
- `tools/build_story.py` : transforme le texte source en `story.js` (texte repris tel quel).
- `tools/art.py` + `tools/generate_images.py` : génèrent une illustration SVG par slide
  dans `images/`, dans un style semi-réaliste commun (modelé en dégradés, textures,
  ombres douces ; mêmes personnages, décors et palette). La description (« prompt ») de chaque image est dans `images/prompts.json`.
- `index.html`, `style.css`, `app.js` : le site.

Le workflow `.github/workflows/pages.yml` régénère et redéploie le site à chaque push
sur la branche par défaut.
Il faut une seule fois activer Pages : **Settings → Pages → Source : GitHub Actions**.

En local :

```bash
python3 tools/build_story.py && python3 tools/generate_images.py
python3 -m http.server
```
