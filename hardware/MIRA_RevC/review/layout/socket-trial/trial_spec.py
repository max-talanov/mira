from pathlib import Path
OUT=Path(__file__).resolve().parent
LAYOUT=OUT.parent
BASE=LAYOUT.parents[1]
SOCKET='ICS-CQFP64-1830-1830-100-1'
SOCKET_REF='J3'
SOCKET_POS=(172.,107.)
ADAPTER=(132.,60.,212.,154.)
CONTROL=(50.,20.,230.,245.)
# Retain the original accessible USB-C edge at Y=158.2; leave a 20mm open cable slot.
CONTROL_PATH=[(50,20),(230,20),(230,245),(110,245),(110,158.2),(90,158.2),(90,245),(50,245)]
PAIRS=[dict(pair='A',control='J1800',module='J1',x=140.,y=102.,angle=90.),dict(pair='B',control='J1801',module='J2',x=204.,y=106.,angle=90.)]
MOUNTS=[('H1800','H1',136.,66.,2.2),('H1801','H2',206.,149.,2.2)]
KEY=('H1802','H3',208.,66.,2.2)
GRIPS=[(152.,60.,192.,70.),(152.,144.,192.,154.)]
REMOVAL=(126.,50.,218.,164.)
LID_APPROX=(148.,72.,196.,143.)
BANK_BL0=(121.,165.,225.,239.)
TILES=[(122.,166.),(175.,166.),(122.,204.5),(175.,204.5)]
TILE_SIZE=(48.,33.5)
