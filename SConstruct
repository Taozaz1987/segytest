from rsf.proj import *

# 1. 读取数据
# WGstack.H 是输入文件，dd form=native 将其转为 RSF 格式
Flow('wgstack', 'WGstack.H', 'dd form=native')

# 2. 构造道头信息
# GeoPlat 需要识别 CDP 号和坐标。
# d2 = 0.0208333 mile ≈ 110 feet (0.0208333 * 5280)
# 我们假设第一道的坐标从 0 开始，CDP 从 1 开始。
Flow('headers', 'wgstack',
     '''
     segyheader 
     tracl=x2+1 
     tracf=x2+1 
     fldr=1 
     cdp=x2+1 
     sx=x2*110 gx=x2*110 
     sy=0 gy=0 
     iline=72 
     xline=x2+1
     ''')
# 注：iline=72 是根据你数据里的 LINE TA-72A 设置的。
# sx 和 gx 设置为相同值（叠加剖面的特性），间距设为 110 (英尺)。

# 3. 写入 SEGY 文件
# 将数据和构造的道头合并，输出为 wgstack.segy
Flow('wgstack.segy', ['wgstack', 'headers'], 'segywrite tfile=${SOURCES[1]}')

# 4. (可选) 进行简单的后处理 - 叠后克希霍夫偏移
# 如果你想在导出前先做个偏移，可以使用你代码里的 kirchinvs
# 这里需要提供一个速度模型，根据你 .H 文件里的 EBCDIC 信息，速度大约在 4900~12100 ft/s 之间。
# 我们简单创建一个常量速度 6000 ft/s 进行演示
Flow('vel', 'wgstack', 'math output=6000')
Flow('stack_mig', ['wgstack', 'vel'], 'kirchinvs velocity=${SOURCES[1]} niter=1')

# 5. 可视化检查
Result('wgstack', 'grey title="Original Stack" label2="Trace Number" unit2=""')
Result('stack_mig', 'grey title="Post-stack Migration" label2="Trace Number" unit2=""')

End()
