#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General Register Calculator
Support for 8/16/32-bit register bit extraction and calculation

Author
2025/12/29 Daniel Chen BU7
"""

import sys
from PyQt5.QtWidgets import QApplication
import RegisterCalcGUI

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = RegisterCalcGUI.RegisterCalcGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()