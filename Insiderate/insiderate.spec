# -*- mode: python -*-
a = Analysis(['insiderate.py'],
             pathex=['C:\\Users\\WantsomeChan\\Code\\EnergyAnalysis\\Insiderate'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='insiderate.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
