
from rsf.proj import *
import rsf.api as rsf


###########################################################################################

def result4 (data, other):
     Result (data,
            '''
            byte clip=1e-2 bar=bar.rsf %s| grey frame1=1000 frame2=280 frame3=380
            title='' label1='Time' unit1='s' label2='Shot domain' unit2='' label3='Receiver domain' unit3=''
            flat=n wantaxis=y wanttitle=n color=g point1=0.85 point2=0.44 screenratio=0.8
            '''%(other))
def result5 (data, other):
     Result (data,
            '''
            byte clip=1e-2 bar=bar.rsf %s| grey3 frame1=1000 frame2=350 frame3=190
            title='' label1='Time' unit1='s' label2='Shot domain' unit2='' label3='Offset domain' unit3=''
            flat=n wantaxis=y wanttitle=n color=g point1=0.85 point2=0.44
            screenratio=0.8
            '''%(other))
# ===================================================================================
#  # Read survey parameter from parameter.txt
# ===================================================================================

Flow ('wgstack', './WGstack.H', 'dd form=native')
result4 ('wgstack', 'screenratio=1 label2="Distance(mile)" ')

wgstack_in = rsf.Input('WGstack.H')
wgstack_n2 = wgstack_in.int('n2')
wgstack_o2 = wgstack_in.float('o2', 0.0)
wgstack_d2 = wgstack_in.float('d2', 1.0)
wgstack_in.close()

# Coordinate unit scaling (set to 1.0 for same units as o2/d2; adjust if needed)
coord_scale = 1.0

Flow(
    'wgstack_tracenum',
    None,
    'spike n1=1 n2=%d | put d2=1 o2=1 | math output="x2" | dd type=int'
    % wgstack_n2,
)
Flow(
    'wgstack_sx',
    None,
    'spike n1=1 n2=%d | put d2=%g o2=%g | math output="x2*%g" | dd type=int'
    % (wgstack_n2, wgstack_d2, wgstack_o2, coord_scale),
)
Flow('wgstack_gx', 'wgstack_sx', 'dd type=int')
Flow(
    'wgstack_cdp',
    None,
    'spike n1=1 n2=%d | put d2=%g o2=%g | math output="(x2-%g)/%g+1" | dd type=int'
    % (wgstack_n2, wgstack_d2, wgstack_o2, wgstack_o2, wgstack_d2),
)
Flow(
    'wgstack_offsets',
    None,
    'spike n1=1 n2=%d | math output="0" | dd type=int'
    % wgstack_n2,
)
Flow(
    'wgstack_headers',
    [
        'wgstack_tracenum',
        'wgstack_sx',
        'wgstack_gx',
        'wgstack_cdp',
        'wgstack_offsets',
    ],
    '''
    segyheader
    tracl=${SOURCES[0]}
    tracf=${SOURCES[0]}
    sx=${SOURCES[1]}
    gx=${SOURCES[2]}
    cdp=${SOURCES[3]}
    offset=${SOURCES[4]}
    ''',
)

Flow('wgstack.segy', ['wgstack', 'wgstack_headers'], 'segywrite tfile=${SOURCES[1]}')






End ()
