import sys
import clr
import pythonnet

print(f"Python version: {sys.version}")
print(f"CLR version: {clr.__version__}")


#pythonnet.load()  # 这一行很重要
clr.AddReference("System.Drawing")              
clr.AddReference("System.Windows.Forms")
# Add a reference to the APx API        
clr.AddReference(r"C:\Program Files\Audio Precision\APx500 4.5\API\AudioPrecision.API2.dll")    #AP路径
clr.AddReference(r"C:\Program Files\Audio Precision\APx500 4.5\API\AudioPrecision.API.dll") 
