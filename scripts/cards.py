"""Project cards for the README: animated particle scenes the same size and layout as the
UN-CREDIBLES cover (title top left, a tag top right). Each card is linked in the README."""
from visuals import THEMES, text, svg
import duel
import skater

W, H = 1180, 300
# (file slug, title, tags, scene, accessible description)
CARDS = (
    ('roller-hunter', 'ROLLER HUNTER', 'SHOOTER · ROGUELIKE', skater.scene,
     'the hero of the trailer\'s comic skates in and hits two demons with slingshot stones, the second from the top of a jump; they burst into particles and he skates off'),
    ('fps-online', 'FPS ONLINE', 'MULTIPLAYER · FPS', duel.scene,
     'two particle soldiers with AKs shoot at each other from behind cover, die and respawn'),
)

def card(theme, slug, title, tags, scene, about):
    c = THEMES[theme]
    b = [text(32, 40, title, c['text'], 18, weight=700), text(32 + len(title) * 11 + 16, 40, tags, c['muted'], 12, weight=700),
         # the whole image is the link, so the corner only says where it goes
         text(W - 32, 40, '> VIEW ON THE ROOKIES', c['accent'], 13, 'end', 700)]
    b += scene(c)
    return svg(W, H, theme, f'{title}: {about}. View on The Rookies.', b)

def render_all():
    """{file name: svg} for every card and theme."""
    return {f'card-{slug}-{theme}.svg': card(theme, slug, *rest)
            for slug, *rest in CARDS for theme in THEMES}
