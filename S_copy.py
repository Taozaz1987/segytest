#==================================================================================
#    Copyright (C) 2025 Chengdu University of Technology.
#    Copyright (C) 2025 Shaohuan Zu.
#
#    Filename：SConstruct
#    Author：Shaohuan Zu
#    Institute：Chengdu University of Technology
#    Email：zushaohuan19@cdut.edu.cn
#    Created  date： 2025-10-30 13:13:07
#    Last modified:  2026-01-07 10:59:10
#    Function：
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or an later version.
# #=================================================================================
# import sys, os, platform
# if 'macos' in platform.platform().lower():
#     myprog_path='/Users/zsh/Documents/cdut_zsh_group/python/subfuctions'
# elif 'linux' in platform.platform().lower():
#     if os.path.exists('/etc/centos-release'):
#         myprog_path='/nfs_data/home/zsh/documents/cdut_zsh_group/python/subfuctions'
#     else:
#         myprog_path='/home/zsh/documents/cdut_zsh_group/python/subfuctions'
# else:
#     myprog_path='F:/linux_backup/home/cdut_zsh_group/python/subfuctions'
# sys.path.append(myprog_path)
# from myprog import *
#
from rsf.prog import *
import rsf.api as rsf


###########################################################################################

def result4 (data, other):
     Result (data,
            '''
            byte clip=1e-2 bar=bar.rsf %s| grey3 frame1=1000 frame2=280 frame3=380
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
result ('wgstack', 'screenratio=1 label2="Distance(mile)" ')

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


#
#
# with open('../Forward_RTM/parameter.txt','r') as file:
#     lines = file.readlines()
# parameter = {
#         'nx':int(lines[1]), # 读取速度模型长度
#         'nz':int(lines[3]), # 读取速度模型深度
#         'pml':int(lines[5]), # 读取吸收边界层数
#         'Lc':int(lines[7]),  # 读取差分阶数
#         'dx':float(lines[9]), # 读取速度模型横向间隔
#         'dz':float(lines[11]), # 读取速度模型纵向间隔
#         'itmax':float(lines[13]), # 读取最大时间
#         'dt':float(lines[15]), # 读取时间间隔
#         'f0':float(lines[17]), # 读取子波主频
#         'ns':int(lines[19]), # 读取炮点数
#         'sx0':float(lines[21]), # 读取炮点起始位置
#         'shotdx':float(lines[23]), # 读取炮点间隔
#         'shotdep':float(lines[25]), # 读取炮点深度
#         'r_n':int(lines[27]), # 读取检波点数
#         'rx0':float(lines[29]), # 读取检波点起始位置
#         'recdx':float(lines[31]), # 读取检波点间隔
#         'recdep':float(lines[33]), # 读取检波点深度
#         'simu':int(lines[35]),  # 是否是多震源系统
#         's_distance':float(lines[37]), # 多震源系统震源间距
#         'save_wf':int(lines[39]), # 是否保存波场快照
#         'inter_wf':int(lines[41]), # 波场快照间隔
#         'v_file':str(lines[43][2:-1]), # 读取速度模型文件
#         'den_file':str(lines[45][2:-1]), # 读取数据文件
#         }
# # 计算偏移距间隔  炮间距或检波点间距中的最小值
# prx = np.arange(parameter['rx0'], parameter['r_n']*parameter['recdx']+parameter['rx0'], parameter['recdx'])
# prxs1 = np.tile(prx, 1*parameter['ns'])
# # prxs2 = np.tile(prx, 1*parameter['ns'])
# # prxs = np.concatenate((prxs1, prxs2), axis=0)
# prxs = prxs1
#
# psx1 = np.arange(parameter['sx0'], parameter['ns']*parameter['shotdx']+parameter['sx0'], parameter['shotdx'])
# psxs1 = np.repeat(psx1, parameter['r_n'], axis=0)
# psxs = psxs1
# # psx2 = np.arange(parameter['sx0']+parameter['s_distance'], parameter['ns']*parameter['shotdx']+parameter['sx0']+parameter['s_distance'], parameter['shotdx'])
# # psxs2 = np.repeat(psx2, parameter['r_n'], axis=0)
# # psxs = np.concatenate((psxs1, psxs2), axis=0)
# #
# pcdpxs = (psxs+prxs)/2
# poffsets = (psxs-prxs)
# cdp = np.unique(pcdpxs)
# offsets = np.unique(poffsets)
# ncdp = len(cdp)
# noffset = len(offsets)
#
# # 计算cdpdx和offsetdx
# parameter['cdpdx']= (int) (np.min(np.diff(cdp)))
# parameter['offsetdx']= (int) (np.min(np.diff(offsets)))
# # parameter['shotdx_simu']= (int) (np.min(np.diff(np.sort(np.unique(psxs),axis=0))))
# # parameter['ns_simu'] = 2*parameter['ns']
#
# # print (parameter['v_file'].split("/")[2][3:-5])
#
# # ===================================================================================
# # Generate seismic survey according to parameter.txt
# # ===================================================================================
# sources = []
# receivers= []
# # 计算道头中炮点和检波点的坐标
# # sx 维度 748 X 1
# # rx 维度 1   X 760
# Flow ('receiver',None, 'spike n1=1 n2=%d |put d2=1|math output="x2+1"'%(parameter['r_n']))
# Flow ('cross', None, 'spike n1=1 n2=%d|put d2=1|math "output=1"'%parameter['r_n'])
# Flow ('source', None, 'spike n1=1 n2=%d|put d2=1|math "output=x2+1"|transp'%(parameter['ns']))
#
# for i in range (parameter['r_n']):
#     sources.append('source')
# for i in range (parameter['ns']):
#     receivers.append('receiver')
# # 炮点排列形式      1 1 1 1 1 2 2 2 2 2 3 3 3 3 3
# # 检波点排列形式    1 2 3 1 2 3 1 2 3 1 2 3 1 2 3
# Flow ('sources', sources, 'cat axis=2 ${SOURCES[1:%d]}|transp|put n1=1 n2=%d d2=1|dd type=int'%(len(sources),parameter['r_n']*parameter['ns']))
# Flow ('receivers', receivers, 'cat axis=2 ${SOURCES[1:%d]}|put d1=1 d2=1|dd type=int'%len(receivers))
# Flow ('fsources', 'sources', 'dd type=float')
# Flow ('freceivers', 'receivers', 'dd type=float')
#
# Flow ('sxs', 'fsources', 'math output="(in-1)*%d+%d"|dd type=int'%(parameter['shotdx'],parameter['sx0']))
# Flow ('rxs', 'freceivers', 'math output="(in-1)*%d+%d"|dd type=int'%(parameter['recdx'],parameter['rx0']))
# Flow ('sys', 'sxs', 'dd type=float|math output="1"|dd type=int')
# Flow ('rys', 'rxs', 'dd type=float|math output="1"|dd type=int')
#
# Flow ('inlines', None, 'spike n1=1 n2=%d|put d2=1|math output="1"|dd type=int' %(parameter['r_n']*parameter['ns']))
# Flow ('xlines', None, 'spike n1=1 n2=%d|put d2=1|math output="1"| dd type=int' %(parameter['r_n']*parameter['ns']))
# # 偏移距等于炮点坐标减去建波点坐标
# Flow ('offsets', 'sxs rxs', 'add scale=1,-1 ${SOURCES[1]}|dd type=int')
# # 由于道头信息都是整数，所以需要将道头信息转换为浮点型进行操作
# Flow ('fsxs', 'sxs', 'dd type=float')
# Flow ('frxs', 'rxs', 'dd type=float')
# # 计算共深度点或共中心点
# Flow ('cdpxs', 'fsxs frxs', 'math in1=${SOURCES[1]} output="(in+in1)/2"|dd type=int')
# Flow ('cdps', 'fsxs frxs', 'math in1=${SOURCES[1]} output="(in+in1)/2/((%d+%d)/4)"|dd type=int'%(parameter['shotdx'],parameter['recdx']))
# # ===================================================================================
# #  Read common shot gathers generated from Forward_RTM
# # ===================================================================================
# # 读取二进制地震数据并设置对于的物理信息，如炮间距、道间距、采样间隔等
# # subpath = parameter['v_file'].split("/")[2][3:-5]2
#
#
# file_num = os.getcwd().split('/')[-1].split('_')[-1]
# subpath='%s_model'%file_num
# subpath='270_767'
# print (subpath)
# path = '../Forward_RTM/forward_output_%s/'%subpath
# csgs=[]
# csgs_cut=[]
# for i in range (parameter['ns']):
#     csg = 'csg%d'%(i+1)
#     csg_cut = 'csg_cut%d'%(i+1)
#     if parameter['simu']==1:
#         Flow (csg, path+'%dsource_seismogram_simu.bin'%(i+1),'bin2rsf n1=%d n2=%d|put d1=%f d2=%d o2=%d|window n1=%d'%(parameter['itmax']/parameter['dt'],parameter['r_n'],parameter['dt'],parameter['recdx'],parameter['rx0'],3000))
#     else:
#         Flow (csg, path+'%dsource_seismogram.bin'%(i+1),'bin2rsf n1=%d n2=%d|put d1=%f d2=%d o2=%d|window n1=%d|noise seed=%d range=0'%(parameter['itmax']/parameter['dt'],parameter['r_n'],parameter['dt'],parameter['recdx'],parameter['rx0'],3000,i))
#     Flow (csg_cut, csg, 'mutter x0=%d v0=%d t0=0.08'%(int(i*parameter['shotdx']+parameter['sx0']),1500*int(parameter['recdx']/parameter['dx'])))
#     # Flow (csg_dir, [csg,csg_cut], 'add scale=1,-1 ${SOURCES[1]}')
#     # result (csg ,'clip=1e-3')
#     # if i<10:
#     # result (csg_cut ,'clip=1e-3')
#     # # result (csg_dir ,'clip=1e-2')
#     csgs.append(csg)
#     csgs_cut.append(csg_cut)
# Flow ('csgs', csgs_cut, 'cat axis=2 ${SOURCES[1:%d]}'%len(csgs_cut))
#
# # 利用计算的炮点、检波点、偏移距、inline、xline和共深度点信息制作segy道头
# Flow ('tdata', 'csgs sxs sys rxs rys offsets inlines xlines cdpxs cdps sources receivers',
#       '''
#       segyheader sx=${SOURCES[1]} sy=${SOURCES[2]} gx=${SOURCES[3]} gy=${SOURCES[4]} offset=${SOURCES[5]}
#       iline=${SOURCES[6]} xline=${SOURCES[7]} cdpx=${SOURCES[8]} cdp=${SOURCES[9]}
#       fldr=${SOURCES[10]} tracf=${SOURCES[11]}
#       ''')
# # 使用炮点和共中心点信息对地震数据进行分选，选择关键字时要设置对应的采样间隔，其中ykey维度在三维显示正对观测者, xkey维度在三维显示的侧面
#
# if parameter['recdx'] <= parameter['shotdx']:
#     domain='sx'
#     Flow ('3ddata', 'csgs tdata', 'intbin4 head=${SOURCES[1]} xkey=21 dx=%d ykey=71 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['shotdx'], parameter['cdpdx'] ) )
#     Flow ('t3data', 'tdata tdata', 'intbin4 head=${SOURCES[1]} xkey=21 dx=%d ykey=71 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['shotdx'],parameter['cdpdx']) )
#     Flow ('3ddata_offset_%s'%domain, 'csgs tdata', 'intbin4 head=${SOURCES[1]} xkey=11 dx=%d ykey=21 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['offsetdx'], parameter['shotdx']))
# else:
#     domain='gx'
#     Flow ('3ddata', 'csgs tdata', 'intbin4 head=${SOURCES[1]} xkey=23 dx=%d ykey=71 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['recdx'], parameter['cdpdx'] ) )
#     Flow ('t3data', 'tdata tdata', 'intbin4 head=${SOURCES[1]} xkey=23 dx=%d ykey=71 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['recdx'],parameter['cdpdx']) )
#     Flow ('3ddata_offset_%s'%domain, 'csgs tdata', 'intbin4 head=${SOURCES[1]} xkey=11 dx=%d ykey=23 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['offsetdx'], parameter['recdx']))
#
# #使用炮点和检波点信息对地震数据进行分选
# Flow ('3ddata_gx_sx', 'csgs tdata', 'intbin4 head=${SOURCES[1]} xkey=23 dx=%d ykey=21 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['recdx'],parameter['shotdx']))
# # result3d ('3ddata_gx_sx','',  'frame2=200 label2="Receiver domain" frame3=200 label3="Shot domain"')
# # 使用偏移距和炮点信息对地震数据进行分选
# # result4 ('3ddata', ' label2="%s domain" label3= "CDP domain" '%domain)
# # result3d ('3ddata_offset_%s'%domain, '', 'label2="%s domain" label3="Offset domain"'%domain)
#
#
# # # #===================================================================================
# # # #  sort data into CDP or CMP
# # # #===================================================================================
# v0       = 1500
# nv       = 201
# dv       = 20
# vp_picks = []
# mucdps   = []
# heads    = []
#
# # 由于分选的CDP道集中有效道数不同，CMP号起和结束时道数非常少，因此设置CMP起始和终止点，避免道数不足导致速度谱不准
# beg1     = 20
# # jump1主要是为了计算速度谱时的速度谱间隔，减少计算量
# jump1    = 5
# ns =1
# for i in range (beg1, ncdp-beg1,jump1):
#     mucdp     = 'mucdp%d'%(i+1)
#     rms       = 'rms_%d'%(i+1)
#     cdpoffset = 'cdpoffset%d'%(i+1)
#     vsvel     = 'vsvel%d'%(i+1)
#     vp_pick   = 'vp_pick%d'%(i+1)
#     head      = 'head%d'%(i+1)
#     #  从三维道头矩阵中读取对应的CDP数据的道头信息
#     Flow (head,'t3data','window f3=%d n3=1'%i)
#     # 提取对应的偏移剧信息
#     Flow (cdpoffset, head, 'window f1=11 n1=1|dd type=float')
#     # 读取对应的CMP数据，并将直达波切除， 其中切除的x0、v0和t0需要根据实际情况进行调整
#     Flow (mucdp, '3ddata', 'window f3=%d n3=1'%i)
#     # result (mucdp, 'clip=1.5e-2')
#     # 对切除直达波的CDP数据计算速度
#     Flow (vsvel, [mucdp, cdpoffset],
#     '''
#     agc|
#     vscan half=n v0=%d nv=%d dv=%d nb=5 ns=%d type=sembl  str=0.5 offset=${SOURCES[1]}|
#     smooth rect1=3 rect2=3|
#     mutter x0=%d t0=1.5 v0=800 inner=y|
#     mutter x0=%d t0=0 v0=2000 inner=n
#     '''%(v0,nv,dv,ns,v0,v0))
#     # Flow (vsvel, [mucdp, cdpoffset], 'vscan half=n v0=%d nv=%d dv=%d nb=5 type=power  str=0.1 offset=${SOURCES[1]}|mutter x0=%d t0=1.5 v0=800 inner=y'%(v0,nv,dv,v0))
#     Plot(vsvel, 'grey color=j allpos=y title="" label1="Time" unit1="s"  unit2="m/s" screenratio=1.8 label="Times(s)" min2=%d max2=%d pclip=99.9 '%(v0,v0+nv*dv))
#     # 从速度谱中提取速度谱最大值对应的速度值
#     # ===================================================================================
#     # pick 中rect1 半径大 可以增加拾取速度谱的平滑性，另外可以对上面速度谱进行切除处理，保留有效能量团再进行拾取
#     # ===================================================================================
#     Flow (vp_pick, vsvel, 'pick rect1=30 rect2=10')
#     Plot (vp_pick, 'graph yreverse=y transp=y plotcol=7 plotfat=7 pad=n  wantaxis=n wanttitle=n screenratio=1.8 min2=%d max2=%d'%(v0,v0+nv*dv))
#     if (i%100==0):
#         result (mucdp, 'clip=2e-3 screenratio=1.8')
#         Result ('pick_vel%d'%(i+1),[vsvel],'Overlay')
#         # Result ('pick_vel1_%d'%(i+1),[vsvel1,vp_pick1],'Overlay')
#         Flow (mucdp+'.dat', mucdp, 'rsf2bin')
#         Flow (vsvel+'.dat', vsvel, 'rsf2bin')
#     vp_picks.append(vp_pick)
#     mucdps.append(mucdp)
#     heads.append(head)
#
#
# # 将计算的一维速度谱信息合并成二维速度谱，主要是当jump1大于1时，需要将速度谱信息合并成二维速度谱
# Flow ('vp_rms',vp_picks,'cat axis=2 ${SOURCES[1:%d]}'%(len(vp_picks)))
# # 显示二维速度谱的速度谱信息
# #result ('vp_rms', 'color=j clip=6000 bias=3000 screenratio=0.5 label2="CDP" ')
# # 当jump1大于1时，则计算的速度谱的间隔是 jump1*parameter['cdpdx']，因此需要将速度谱的间隔调整为parameter['cdpdx']
# # index1 等于1 ，主要是为了数据分选构建道头信息
# Flow ('index1', 'vp_rms', 'window n1=1|math "output=1"|dd type=int')
# Flow ('index2', '3ddata', 'window n1=1 f2=1 n2=1|math output="x1"|window f1=%d n1=%d j1=%d |dd type=int'%(beg1,len(range(beg1,ncdp-beg1,int(jump1/ns))),int (jump1/ns)))
#
# # 根据抽取的CDP道集信息构建道头
# Flow ('headss', 'vp_rms index1 index1 index1 index1 index1 index2',
#       '''
#       segyheader sx=${SOURCES[6]} gx=${SOURCES[6]} offset=${SOURCES[3]}
#       iline=${SOURCES[4]} xline=${SOURCES[5]} cdpx=${SOURCES[6]}
#       ''')
# # 利用构建的道头信息对速度谱进行分选，目的是当jump1大于1时，将计算的速度谱放置在正确的位置上
# Flow ('vp_rms_pad', 'vp_rms headss', 'intbin4 head=${SOURCES[1]} xkey=71 dx=%d  ykey=11 dy=1 rkey=73 dr=1 skey=74 ds=1'%(parameter['cdpdx']))
# #result ('vp_rms_pad', 'color=j clip=6000 bias=300 screenratio=0.5 label2="CDP" ')
#
# # 当jump1大于1时，利用已有速度谱值复制到相邻道集上 假设有速度谱的道号是 5  10  15
# # 则将数据复制为5份，将原位置的速度谱复制到1 6 11， 2 7 12， 3 8 13， 4 9 14上， 然后将5组数据进行叠加
# vps = []
# for i in range (jump1):
#     vp= 'vp_%d'%i
#     Flow (vp, 'vp_rms_pad', 'window f2=%i |pad end2=%d'%(i,i))
#     vps.append(vp)
# Flow ('vps', vps, 'cat axis=3 ${SOURCES[1:%d]}'%len(vps))
# # 得到复制后的速度谱
# Flow ('vp_rms_pad1', 'vps', 'stack axis=3')
#
# #result ('vp_rms_pad1', 'color=j clip=3000 bias=1900 screenratio=0.5 label2="CDP" ')
# # 将复制道集后的速度谱进行平滑处理
# Flow ('vp_rms_pad_smooth', 'vp_rms_pad1', 'smooth rect2=25 repeat=3')#
# result ('vp_rms_pad_smooth', 'color=j clip=6000 bias=3000 screenratio=0.5 label2="CDP" ')
# # # # # ===================================================================================
# # # # # ========6 Applied NMO to CDP data with smoothed velocity===========================
# # # # # ========7 Mued NMO strecthing larger 0.5===========================================
# # # # # ===================================================================================
#
# nmos = []
# for i in range (beg1,ncdp-beg1-jump1+1):
#     cdpoffsett = 'cdpoffsett%d'%(i+1)
#     mucdpp = 'mucdpp%d'%(i+1)
#     rms = 'vp_rms_smooth_%d'%(i+1)
#     nmo = 'nmo%d'%(i+1)
#      #  从三维道头矩阵中读取对应的CDP数据的道头信息
#     # 提取对应的偏移剧信息
#     Flow (cdpoffsett, 't3data', 'window  f1=11 n1=1 f3=%d n3=1|dd type=float'%i)
#     # 读取对应的CMP数据，并将直达波切除， 其中切除的x0、v0和t0需要根据实际情况进行调整
#     Flow (mucdpp, '3ddata', 'window f3=%d n3=1'%(i))
# #   dpoffset = 'cdpoffset%d'%(i+1)
#     # 从平滑后的二维速度谱中抽取对应的一维速度谱值 ，由于二维速度谱的n2 小于CDP道集数量，因此此时是i-beg1
#     Flow (rms, 'vp_rms_pad_smooth', 'window f2=%d n2=1|put d2=10'%(i-beg1))
#     # ===================================================================================
#     # ======== 偏移距大时 会存在东郊拉伸现象，可以使用 nmo str控制，另外可以使用mutter 进行切除
#     # ===================================================================================
#     Flow (nmo, [mucdpp, cdpoffsett, rms], 'nmo offset=${SOURCES[1]} velocity=${SOURCES[2]} half=n str=0.7|mutter x0=%d v0=3000 t0=-0.2'%(parameter['sx0']/2+i*parameter['cdpdx']))
#
#     if (i%100)==0:
#         # 反动校正
#         # Flow ('i'+nmo, [nmo, rms, cdpoffsett], 'inmo velocity=${SOURCES[1]} half=n offset=${SOURCES[2]}')
#         # result (mucdpp,'clip=6e-3')
#         result (nmo,'clip=6e-3')
#         # Flow (mucdpp+'.dat', mucdpp, 'rsf2bin')
#         Flow (nmo+'.dat', nmo, 'rsf2bin')
#     nmos.append(nmo)
# # 得到的NMO道集是按照CDP号进行排列的
# Flow ('nmos', nmos, 'cat axis=3 ${SOURCES[1:%d]}'%len(nmos))
# # result ('nmos','clip=2e-3 screenratio=1.8 label2="CDP" ')
# Flow ('nmos.dat', 'nmos', 'rsf2bin')
# # result3 ('nmos', 'frame2=190 frame3=300')
# # # # ===================================================================================
# # # # =========8 Stack along offset to obtain stacked profile============================
# # # # ===================================================================================
# #将NMO道集按照偏移距进行叠加
# Flow ('stack', 'nmos', 'stack axis=2 norm=n')
# # Flow ('demul_stack', 'demul_nmos', 'stack axis=2 norm=n')
# path = os.getcwd()
# temp = [path.split('/')[-2],path.split('/')[-1]]
# prefix='_'.join(temp)
#
# Flow (prefix+'_stack.dat', 'stack', 'rsf2bin')
# result ('stack','clip=5e-1 screenratio=.8 label2="CDP"')
#
# # Flow ('t3data', 'tdata tdata', 'intbin4 head=${SOURCES[1]} xkey=21 dx=%d ykey=71 dy=%d rkey=73 dr=1 skey=74 ds=1'%(parameter['shotdx'],parameter['cdpdx']) )
# if parameter['recdx'] <= parameter['shotdx']:
#     Flow ('tdata_cdp_offset', 'tdata tdata', 'intbin4 head=${SOURCES[1]} xkey=71 dx=%d ykey=21 dy=%d ymin=0 ymax=0 rkey=73 dr=1 skey=74 ds=1'%(parameter['cdpdx'],parameter['shotdx']) )
# else:
#     Flow ('tdata_cdp_offset', 'tdata tdata', 'intbin4 head=${SOURCES[1]} xkey=71 dx=%d ykey=23 dy=%d ymin=0 ymax=0 rkey=73 dr=1 skey=74 ds=1'%(parameter['cdpdx'],parameter['recdx']) )
#
# Flow ('head2segy', 'tdata_cdp_offset', 'window f2=%d n2=%d'%(beg1,ncdp-2*beg1-jump1+1))
# Flow ('stack.segy', 'stack head2segy', 'segywrite tfile=${SOURCES[1]}')
# # # ===================================================================================
# # # ========9 Apply Kichhoff 2D post-stack least-squares time migration================
# # # ===================================================================================
# #叠后克希霍夫积分偏移处理
# Flow ('stack_kif ', 'stack vp_rms_pad_smooth',
#      '''kirchinvs velocity=${SOURCES[1]} hd=y  niter=1 liter=3 ps=1 verb=1''')
# result ('stack_kif','clip=1e-2 screenratio=0.8 label2="CDP"')
#
# Flow (prefix+'_stack_kif.dat', 'stack_kif', 'rsf2bin')
#
#



End ()
