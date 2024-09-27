import sys, clr, pythonnet  #导入库

clr.AddReference("System.Drawing")              
clr.AddReference("System.Windows.Forms")
# Add a reference to the APx API        
clr.AddReference(r"C:\Program Files\Audio Precision\APx500 4.5\API\AudioPrecision.API2.dll")    #AP路径
clr.AddReference(r"C:\Program Files\Audio Precision\APx500 4.5\API\AudioPrecision.API.dll") 
