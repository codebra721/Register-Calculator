import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QLabel, QLineEdit, 
                             QPushButton, QRadioButton, QTextEdit, QComboBox,
                             QMessageBox, QButtonGroup, QSplitter, QFileDialog,
                             QDialog, QListWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import csv
from datetime import datetime
import RegisterCalculator

class RegisterCalcGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.calc = RegisterCalculator.RegisterCalculator()
        self.csv_data = []  # CSV Data List
        self.current_result = None  # Current calculation result
        self.current_original = None  # Current register raw value
        self.last_formula_result = None
        self.converting = False  # Prevent infinite loop during conversion
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('General Register Calculator v1.0')
        self.setGeometry(100, 100, 900, 700)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # ===== Register Inputarea =====
        input_group = QGroupBox("Register Input")
        input_layout = QVBoxLayout()
        
        # Bit width selection
        bit_layout = QHBoxLayout()
        bit_layout.addWidget(QLabel("Bit Width:"))
        
        self.bit_group = QButtonGroup()
        self.radio_8bit = QRadioButton("8-bit")
        self.radio_16bit = QRadioButton("16-bit")
        self.radio_32bit = QRadioButton("32-bit")
        self.radio_16bit.setChecked(True)
        
        self.bit_group.addButton(self.radio_8bit, 8)
        self.bit_group.addButton(self.radio_16bit, 16)
        self.bit_group.addButton(self.radio_32bit, 32)
        
        bit_layout.addWidget(self.radio_8bit)
        bit_layout.addWidget(self.radio_16bit)
        bit_layout.addWidget(self.radio_32bit)
        bit_layout.addStretch()
        
        input_layout.addLayout(bit_layout)
        
        # Register valueinput
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Register value:"))
        self.reg_value_input = QLineEdit("0x")
        self.reg_value_input.setMaximumWidth(200)
        self.reg_value_input.textChanged.connect(self.on_reg_value_changed)
        value_layout.addWidget(self.reg_value_input)
        
        value_layout.addWidget(QLabel("⇄"))
        
        value_layout.addWidget(QLabel("Decimal:"))
        self.dec_display = QLineEdit()
        self.dec_display.setPlaceholderText("Decimal display")
        self.dec_display.setMaximumWidth(200)
        self.dec_display.textChanged.connect(self.on_dec_display_changed)
        value_layout.addWidget(self.dec_display)
        
        value_layout.addStretch()
        
        input_layout.addLayout(value_layout)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # ===== Bit Extractionarea =====
        extract_group = QGroupBox("Bit Extraction")
        extract_layout = QVBoxLayout()
        
        bit_range_layout = QHBoxLayout()
        bit_range_layout.addWidget(QLabel("Start bit:"))
        self.start_bit_input = QLineEdit("0")
        self.start_bit_input.setMaximumWidth(80)
        bit_range_layout.addWidget(self.start_bit_input)
        
        bit_range_layout.addWidget(QLabel("End bit:"))
        self.end_bit_input = QLineEdit("7")
        self.end_bit_input.setMaximumWidth(80)
        bit_range_layout.addWidget(self.end_bit_input)
        
        self.extract_btn = QPushButton("Extract Bits")
        self.extract_btn.clicked.connect(self.extract_bits)
        self.extract_btn.setStyleSheet("background-color: #C8E6C9; color: black; font-weight: bold;")
        bit_range_layout.addWidget(self.extract_btn)
        bit_range_layout.addStretch()
        
        extract_layout.addLayout(bit_range_layout)
        extract_group.setLayout(extract_layout)
        main_layout.addWidget(extract_group)
        
        # ===== Result display area =====
        result_group = QGroupBox("Extraction")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier", 10))
        self.result_text.setMinimumHeight(250)
        
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
        
        # ===== Save button area =====
        save_group = QGroupBox("Storage & Management")
        save_layout = QHBoxLayout()
        
        save_layout.addWidget(QLabel("Save to:"))
        
        self.save_index_combo = QComboBox()
        self.save_index_combo.addItems([str(i) for i in range(10)])
        self.save_index_combo.setMaximumWidth(60)
        save_layout.addWidget(self.save_index_combo)
        
        self.save_to_a_btn = QPushButton("Save Value")
        self.save_to_a_btn.clicked.connect(self.save_to_A)
        self.save_to_a_btn.setStyleSheet("background-color: #BBDEFB; color: black;")
        save_layout.addWidget(self.save_to_a_btn)
        
        self.list_a_btn = QPushButton("List Save Value")
        self.list_a_btn.clicked.connect(self.list_A_array)
        self.list_a_btn.setStyleSheet("background-color: #FFE0B2; color: black;")
        save_layout.addWidget(self.list_a_btn)

        self.clear_a_btn = QPushButton("Clear Save Value")
        self.clear_a_btn.clicked.connect(self.clear_A_array)
        self.clear_a_btn.setStyleSheet("background-color: #FFCDD2; color: black;")
        save_layout.addWidget(self.clear_a_btn)
        
        save_layout.addStretch()
        
        save_group.setLayout(save_layout)
        main_layout.addWidget(save_group)
        
        # ===== Formula Calculationarea =====
        formula_group = QGroupBox("Formula Calculation")
        formula_layout = QVBoxLayout()
        
        # Formula input
        formula_input_layout = QHBoxLayout()
        formula_input_layout.addWidget(QLabel("formula:"))
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("e.g.: 2^v - 148  or  a0 * a1 / 100")
        formula_input_layout.addWidget(self.formula_input)
        formula_layout.addLayout(formula_input_layout)
        
        # Formula description
        formula_help = QLabel(
            "Supported variables: v (Current extraction value), a0~a9 (Value array)\n"
            "Supported operations: +, -, *, /, //, %, ^ (power)\n"
            "Supported functions: abs, round, pow, sqrt, log, sin, cos, tan, pi, e"
        )
        formula_help.setStyleSheet("color: #666; font-size: 9pt;")
        formula_layout.addWidget(formula_help)
        
        # Formula buttons
        formula_btn_layout = QHBoxLayout()
        
        self.calc_formula_btn = QPushButton("Calculate Formula")
        self.calc_formula_btn.clicked.connect(self.calculate_formula)
        self.calc_formula_btn.setStyleSheet("background-color: #C8E6C9; color: black; font-weight: bold;")
        formula_btn_layout.addWidget(self.calc_formula_btn)
        
        formula_btn_layout.addWidget(QLabel("Save formula to:"))
        self.formula_index_combo = QComboBox()
        self.formula_index_combo.addItems([str(i) for i in range(10)])
        self.formula_index_combo.setMaximumWidth(60)
        formula_btn_layout.addWidget(self.formula_index_combo)
        
        self.save_formula_btn = QPushButton("Save formula")
        self.save_formula_btn.clicked.connect(self.save_formula)
        self.save_formula_btn.setStyleSheet("background-color: #BBDEFB; color: black;")
        formula_btn_layout.addWidget(self.save_formula_btn)
        
        self.load_formula_btn = QPushButton("Load Formula")
        self.load_formula_btn.clicked.connect(self.load_formula)
        self.load_formula_btn.setStyleSheet("background-color: #C5CAE9; color: black;")
        formula_btn_layout.addWidget(self.load_formula_btn)
        
        self.list_formula_btn = QPushButton("List Save Formula")
        self.list_formula_btn.clicked.connect(self.list_F_array)
        self.list_formula_btn.setStyleSheet("background-color: #FFE0B2; color: black;")
        formula_btn_layout.addWidget(self.list_formula_btn)
        
        self.clear_f_btn = QPushButton("Clear Save Formula")
        self.clear_f_btn.clicked.connect(self.clear_F_array)
        self.clear_f_btn.setStyleSheet("background-color: #FFCDD2; color: black;")
        formula_btn_layout.addWidget(self.clear_f_btn)
        
        formula_btn_layout.addStretch()
        formula_layout.addLayout(formula_btn_layout)
        
        # Formula Calculationresult
        formula_result_layout = QHBoxLayout()
        formula_result_layout.addWidget(QLabel("Calculate result:"))
        self.formula_result_label = QLabel("No any Calculate")
        self.formula_result_label.setStyleSheet(
            "background-color: #F5F5F5; padding: 10px; "
            "border: 1px solid #CCC; border-radius: 3px; "
            "font-size: 16pt; font-weight: bold;"
        )
        self.formula_result_label.setMinimumHeight(55)
        formula_result_layout.addWidget(self.formula_result_label)
        formula_layout.addLayout(formula_result_layout)
        
        formula_group.setLayout(formula_layout)
        main_layout.addWidget(formula_group)
        

        # ===== CSV Storage area =====
        csv_group = QGroupBox("CSV Export")
        csv_layout = QVBoxLayout()
        
        # Input name and selectSource
        csv_input_layout = QHBoxLayout()
        csv_input_layout.addWidget(QLabel("Name:"))
        self.csv_name_input = QLineEdit()
        self.csv_name_input.setPlaceholderText("e.g. VBatt, Rsense...")
        self.csv_name_input.setMaximumWidth(200)  # Reduce name field width
        csv_input_layout.addWidget(self.csv_name_input)
        
        csv_input_layout.addWidget(QLabel("Source:"))
        self.csv_source_btn = QPushButton("Extraction")
        self.csv_source_btn.setCheckable(True)
        self.csv_source_btn.setChecked(False)  # False = Extraction, True = Formula
        self.csv_source_btn.clicked.connect(self.toggle_csv_source)
        self.csv_source_btn.setMaximumWidth(140)
        self.csv_source_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE0B2;
                color: black;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #E1BEE7;
            }
        """)
        csv_input_layout.addWidget(self.csv_source_btn)
        
        self.add_csv_btn = QPushButton("Add to CSV List")
        self.add_csv_btn.clicked.connect(self.add_to_csv)
        self.add_csv_btn.setStyleSheet("background-color: #C8E6C9; color: black; font-weight: bold;")
        csv_input_layout.addWidget(self.add_csv_btn)
        
        csv_input_layout.addStretch()
        csv_layout.addLayout(csv_input_layout)
        
        # From A[] Arrayselect
        csv_array_layout = QHBoxLayout()
        csv_array_layout.addWidget(QLabel("From Value array select from:"))
        self.csv_array_combo = QComboBox()
        self.csv_array_combo.addItems([f"A[{i}]" for i in range(10)])
        self.csv_array_combo.setMaximumWidth(80)
        csv_array_layout.addWidget(self.csv_array_combo)
        
        self.add_from_array_btn = QPushButton("Add to CSV")
        self.add_from_array_btn.clicked.connect(self.add_from_array_to_csv)
        self.add_from_array_btn.setStyleSheet("background-color: #C8E6C9; color: black; font-weight: bold;")
        csv_array_layout.addWidget(self.add_from_array_btn)
        
        csv_array_layout.addStretch()
        csv_layout.addLayout(csv_array_layout)
        
        # buttonarea
        csv_btn_layout = QHBoxLayout()
        

        
        self.view_csv_btn = QPushButton("View CSV List")
        self.view_csv_btn.clicked.connect(self.view_csv_data)
        self.view_csv_btn.setStyleSheet("background-color: #BBDEFB; color: black;")
        csv_btn_layout.addWidget(self.view_csv_btn)
        
        self.export_csv_btn = QPushButton("Export CSV file")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setStyleSheet("background-color: #C8E6C9; color: black;")
        csv_btn_layout.addWidget(self.export_csv_btn)
        
        self.clear_csv_btn = QPushButton("Clear CSV List")
        self.clear_csv_btn.clicked.connect(self.clear_csv_data)
        self.clear_csv_btn.setStyleSheet("background-color: #FFCDD2; color: black;")
        csv_btn_layout.addWidget(self.clear_csv_btn)
        
        csv_btn_layout.addStretch()
        csv_layout.addLayout(csv_btn_layout)
        
        csv_group.setLayout(csv_layout)
        main_layout.addWidget(csv_group)


        # Set overall style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 3px;
                font-size: 11pt;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }
        """)
    
    def parse_value(self, value_str):
        """Parse input value (Support 0x, 0b, Decimal)"""
        value_str = value_str.strip()
        
        try:
            if value_str.startswith('0x') or value_str.startswith('0X'):
                return int(value_str, 16)
            elif value_str.startswith('0b') or value_str.startswith('0B'):
                return int(value_str, 2)
            else:
                return int(value_str, 10)
        except ValueError:
            raise ValueError(f"Cannot parseValue: {value_str}")
    
    def get_bit_width(self):
        """Get currently selected bit width"""
        return self.bit_group.checkedId()
    
    def extract_bits(self):
        """Extract Bitsoperation"""
        try:
            # GetRegister value
            reg_value = self.parse_value(self.reg_value_input.text())
            self.current_original = reg_value
            
            # Check bit width range
            bit_width = self.get_bit_width()
            max_value = (1 << bit_width) - 1
            
            if reg_value > max_value:
                QMessageBox.critical(self, "Error", 
                    f"{bit_width}-bit Register max value is 0x{max_value:X}")
                return
            
            # Get bit range
            start_bit = int(self.start_bit_input.text())
            end_bit = int(self.end_bit_input.text())
            
            if start_bit < 0 or end_bit >= bit_width:
                QMessageBox.critical(self, "Error", 
                    f"Bit range must be within 0 ~ {bit_width-1} and")
                return
            
            # Extract Bits
            extracted = self.calc.extract_bits(reg_value, start_bit, end_bit)
            self.current_result = extracted
            
            # Display result
            self.display_result(reg_value, start_bit, end_bit, extracted, bit_width)
            
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def display_result(self, original, start_bit, end_bit, extracted, bit_width):
            """display Extraction"""
            output = []
            
            num_bits = end_bit - start_bit + 1
            
            output.append("Extraction:")
            output.append(f"  Hexadecimal: 0x{extracted:X}")
            output.append(f"  Decimal:   {extracted}")
            output.append(f"  Binary:   0b{extracted:0{num_bits}b}")
            output.append("")
            
            # Display bit diagram
            output.append("Bit diagram:")
            original_bits = format(original, f'0{bit_width}b')
            
            # For 32-bit, split into two lines for better readability
            if bit_width == 32:
                # Upper half: bit 31-16 (display as F-0)
                output.append("Bit [31:16]")
                
                upper_positions = []
                upper_bits = []
                upper_highlight = []
                for i in range(31, 15, -1):
                    # Display 31-16 as F, E, D, C, ..., 0
                    # i=31 -> F, i=30 -> E, ..., i=16 -> 0
                    display_value = 31 - i  # 0, 1, 2, ..., 15
                    hex_char = f"{15 - display_value:X}"  # F, E, D, ..., 0
                    upper_positions.append(hex_char)
                    upper_bits.append(original_bits[31-i])
                    if start_bit <= i <= end_bit:
                        upper_highlight.append("^")
                    else:
                        upper_highlight.append(" ")
                    if i > 16 and i % 4 == 0:
                        upper_positions.append(" ")
                        upper_bits.append(" ")
                        upper_highlight.append(" ")
                
                output.append(f"  position: {''.join(upper_positions)}")
                output.append(f"  value:    {''.join(upper_bits)}")
                output.append(f"  extract:  {''.join(upper_highlight)}")
                output.append("")
                
                # Lower half: bit 15-0 (display as F-0)
                output.append("Bit [15:0]")
                
                lower_positions = []
                lower_bits = []
                lower_highlight = []
                for i in range(15, -1, -1):
                    # Display 15-0 as F, E, D, C, ..., 0
                    lower_positions.append(f"{i:X}")
                    lower_bits.append(original_bits[31-i])
                    if start_bit <= i <= end_bit:
                        lower_highlight.append("^")
                    else:
                        lower_highlight.append(" ")
                    if i > 0 and i % 4 == 0:
                        lower_positions.append(" ")
                        lower_bits.append(" ")
                        lower_highlight.append(" ")
                
                output.append(f"  position: {''.join(lower_positions)}")
                output.append(f"  value:    {''.join(lower_bits)}")
                output.append(f"  extract:  {''.join(lower_highlight)}")
            
            else:
                # For 8-bit and 16-bit, display in single line with space every 4 bits
                positions = []
                for i in range(bit_width-1, -1, -1):
                    positions.append(f"{i:X}")
                    if i > 0 and i % 4 == 0:
                        positions.append(" ")
                bit_positions = "".join(positions)
                
                # Add space to binary display every 4 bits to match position
                bits_display = []
                for i in range(bit_width):
                    bits_display.append(original_bits[i])
                    if (bit_width - i - 1) > 0 and (bit_width - i - 1) % 4 == 0:
                        bits_display.append(" ")
                bits_with_space = "".join(bits_display)
                
                output.append(f"  position: {bit_positions}")
                output.append(f"  value:    {bits_with_space}")
                
                # Mark extraction range (with space every 4 bits)
                highlight = []
                for i in range(bit_width-1, -1, -1):
                    if start_bit <= i <= end_bit:
                        highlight.append("^")
                    else:
                        highlight.append(" ")
                    if i > 0 and i % 4 == 0:
                        highlight.append(" ")
                highlight_str = "".join(highlight)
                output.append(f"  extract:  {highlight_str}")
            
            self.result_text.setText("\n".join(output))
    
    def save_to_A(self):
        """Save current resultto A[] Array"""
        if self.current_result is None:
            QMessageBox.warning(self, "Warning", "No result calculated yet")
            return
        
        try:
            index = int(self.save_index_combo.currentText())
            self.calc.store_value('A', index, self.current_result)
            QMessageBox.information(self, "Success", 
                f"Saved {self.current_result} to A[{index}]")
            next_index = (index + 1) % 10  # exceeds 9 wrap toto 0
            self.save_index_combo.setCurrentText(str(next_index))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def list_A_array(self):
        """List A[] Array Content"""
        # Create new window
        array_dialog = QMessageBox(self)
        array_dialog.setWindowTitle("A[] Array Content")
        
        output = []
        output.append("=" * 50)
        output.append("A[] Array Content:")
        output.append("=" * 50)
        
        has_content = False
        for i, val in enumerate(self.calc.A):
            if val is not None:
                output.append(f"A[{i}] = {val:12}  (0x{val:X})")
                has_content = True
            else:
                output.append(f"A[{i}] = (Empty)")
        
        output.append("=" * 50)
        
        if not has_content:
            output.append("\n※ Array is currently empty")
        
        array_dialog.setText("\n".join(output))
        array_dialog.setStyleSheet("QLabel{min-width: 400px; font-family: Courier;}")
        array_dialog.exec_()
        
    def clear_A_array(self):
        """Clear A[] Array"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Clear")
        msg_box.setText("Clear all Value at array data?")
        msg_box.setIcon(QMessageBox.Warning)
        
        # Create custom button
        yes_btn = msg_box.addButton("Yes", QMessageBox.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.setDefaultButton(no_btn)
        
        # Set button style
        yes_btn.setStyleSheet("""
            background-color: #BBDEFB;
            color: black;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            font-size: 11pt;
            min-width: 80px;
        """)
        
        no_btn.setStyleSheet("""
            background-color: #FFCDD2;
            color: black;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            font-size: 11pt;
            min-width: 80px;
        """)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == yes_btn:
            self.calc.A = [None] * 10
            self.save_index_combo.setCurrentText("0")  # Reset index to 0
            QMessageBox.information(self, "Success", "Cleared A[] Array")
    
    def calculate_formula(self):
        """Calculate Formula"""
        formula = self.formula_input.text().strip()
        
        if not formula:
            QMessageBox.warning(self, "Warning", "Please enter formula")
            return
        
        try:
            # Use current v
            result = self.calc.calculate_formula(formula, self.current_result)
            
            # Display result
            if isinstance(result, float):
                result_str = f"{result}"
            else:
                result_str = f"{int(result)}"
            
            self.formula_result_label.setText(result_str)
            self.formula_result_label.setStyleSheet(
                "background-color: #C8E6C9; padding: 10px; "
                "border: 2px solid #4CAF50; border-radius: 3px; "
                "font-size: 14pt; font-weight: bold; color: #2E7D32;"
            )
            
            # Update current_result toFormula Calculationresult
            self.last_formula_result = result if isinstance(result, (int, float)) else None
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.formula_result_label.setText("CalculateError")
            self.formula_result_label.setStyleSheet(
                "background-color: #FFCDD2; padding: 10px; "
                "border: 2px solid #F44336; border-radius: 3px; "
                "font-size: 14pt; font-weight: bold; color: #C62828;"
            )
            self.last_formula_result = None
    
    def save_formula(self):
        """Save Formula to F[] Array"""
        formula = self.formula_input.text().strip()
        
        if not formula:
            QMessageBox.warning(self, "Warning", "Please enter formula")
            return
        
        try:
            index = int(self.formula_index_combo.currentText())
            self.calc.store_value('F', index, formula)
            QMessageBox.information(self, "Success", 
                f"Saved formula to F[{index}]:\n{formula}")
            next_index = (index + 1) % 10  # exceeds 9 wrap toto 0
            self.formula_index_combo.setCurrentText(str(next_index))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def load_formula(self):
        """From F[] Array Load Formula"""
        try:
            index = int(self.formula_index_combo.currentText())
            formula = self.calc.F[index]
            
            if formula is None:
                QMessageBox.warning(self, "Warning", f"F[{index}] is empty")
                return
            
            self.formula_input.setText(formula)
            QMessageBox.information(self, "Success", 
                f"Loaded F[{index}] formula:\n{formula}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def list_F_array(self):
        """List F[] Array Content"""
        array_dialog = QMessageBox(self)
        array_dialog.setWindowTitle("F[] Formula arraycontent")
        
        output = []
        output.append("=" * 60)
        output.append("F[] Formula arraycontent:")
        output.append("=" * 60)
        
        has_content = False
        for i, formula in enumerate(self.calc.F):
            if formula is not None:
                output.append(f"F[{i}] = {formula}")
                has_content = True
            else:
                output.append(f"F[{i}] = (Empty)")
        
        output.append("=" * 60)
        
        if not has_content:
            output.append("\n※ Array is currently empty")
        
        array_dialog.setText("\n".join(output))
        array_dialog.setStyleSheet("QLabel{min-width: 500px; font-family: Courier;}")
        array_dialog.exec_()
        
    def clear_F_array(self):
        """Clear F[] Array"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Clear")
        msg_box.setText("Clear all Formula at array data?")
        msg_box.setIcon(QMessageBox.Warning)
        
        # Create custom button
        yes_btn = msg_box.addButton("Yes", QMessageBox.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.setDefaultButton(no_btn)
        
        # Set button style
        yes_btn.setStyleSheet("""
            background-color: #BBDEFB;
            color: black;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            font-size: 11pt;
            min-width: 80px;
        """)
        
        no_btn.setStyleSheet("""
            background-color: #FFCDD2;
            color: black;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            font-size: 11pt;
            min-width: 80px;
        """)
        
        msg_box.exec_()
        if msg_box.clickedButton() == yes_btn:
            self.calc.F = [None] * 10
            self.formula_index_combo.setCurrentText("0")
            QMessageBox.information(self, "Success", "Cleared F[] Array")

    def add_to_csv(self):
        """Add data to CSV list"""
        name = self.csv_name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter name")
            return
        
        # Determine which value to save based on button state
        if self.csv_source_btn.isChecked():
            # Button is pressed = Formula
            value = self.last_formula_result
            source = "Formula"
            if value is None:
                QMessageBox.warning(self, "Warning", "Not yet Calculate Formula")
                return
        else:
            # Button is not pressed = Extraction
            value = self.current_result
            source = "Extraction"
            if value is None:
                QMessageBox.warning(self, "Warning", "Not yet Extract Bits")
                return
        
        # Addto CSV Data List
        self.csv_data.append((name, value))
        
        # clearEmptynameinputbox
        self.csv_name_input.clear()
        
        QMessageBox.information(self, "Success", 
            f"Added:\nName: {name}\nSource: {source}\nValue: {value}")
    
    def view_csv_data(self):
        """View CSV Data List"""
        if not self.csv_data:
            QMessageBox.information(self, "CSV list", "CSV list is currently empty")
            return
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("CSV Data List")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Display count info
        count_label = QLabel(f"Current data: {len(self.csv_data)} records (No limit)")
        count_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2196F3;")
        layout.addWidget(count_label)
        
        # List display
        list_widget = QListWidget()
        list_widget.setFont(QFont("Courier", 10))
        for i, (name, value) in enumerate(self.csv_data):
            list_widget.addItem(f"{i+1:3d}. {name:<30} {value}")
        layout.addWidget(list_widget)
        
        # Button area
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("background-color: #FFCDD2; color: black; padding: 8px 15px;")
        delete_btn.clicked.connect(lambda: self.delete_csv_item(list_widget, dialog, count_label))
        btn_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #E0E0E0; color: black; padding: 8px 15px;")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def delete_csv_item(self, list_widget, dialog, count_label):
        """Delete CSV single record in listrecords"""
        current_row = list_widget.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(dialog, "Warning", "Please select item to delete first")
            return
        
        # Confirm deletion
        name, value = self.csv_data[current_row]
        reply = QMessageBox.question(
            dialog,
            "Confirm deletion",
            f"Delete thisrecords?\n\nName: {name}\nValue: {value}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete data
            del self.csv_data[current_row]
            
            # UpdateList display
            list_widget.clear()
            for i, (name, value) in enumerate(self.csv_data):
                list_widget.addItem(f"{i+1:3d}. {name:<30} {value}")
            
            # Update count label
            count_label.setText(f"Current data: {len(self.csv_data)} records (No limit)")
            
            QMessageBox.information(dialog, "Success", "Deleted CSV Done")
            
            # If list isEmpty,Closedialog
            if len(self.csv_data) == 0:
                dialog.close()
    
    def export_csv(self):
        """Export CSV file"""
        if not self.csv_data:
            QMessageBox.warning(self, "Warning", "CSV list is empty, cannot export")
            return
        
        # Open file dialog
        default_filename = f"register_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            default_filename,
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not filename:
            return  # User cancelled
        
        try:
            # Write CSV Files
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['name', 'Value'])
                # Write data
                writer.writerows(self.csv_data)
            
            QMessageBox.information(self, "Success", 
                f"Exported {len(self.csv_data)} records to:\n{filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def clear_csv_data(self):
        """Clear CSV Data List"""
        if not self.csv_data:
            QMessageBox.information(self, "Info", "CSV List is empty")
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Clear")
        msg_box.setText(f"Clear {len(self.csv_data)} CSV records?")
        msg_box.setIcon(QMessageBox.Warning)
        
        # Create custom button
        yes_btn = msg_box.addButton("Yes", QMessageBox.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.setDefaultButton(no_btn)
        
        # Set button style
        yes_btn.setStyleSheet("""
            background-color: #BBDEFB;
            color: black;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            font-size: 11pt;
            min-width: 80px;
        """)
        
        no_btn.setStyleSheet("""
            background-color: #FFCDD2;
            color: black;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            font-size: 11pt;
            min-width: 80px;
        """)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == yes_btn:
            self.csv_data.clear()
            QMessageBox.information(self, "Success", "Cleared CSV Data List")
    
    def toggle_csv_source(self):
        """Toggle CSV Sourcebutton text"""
        if self.csv_source_btn.isChecked():
            # ToggletoFormula
            self.csv_source_btn.setText("Formula")
        else:
            # ToggletoExtraction
            self.csv_source_btn.setText("Extraction")
    
    def add_from_array_to_csv(self):
        """From A[] ArrayAdd datato CSV list"""
        name = self.csv_name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter name")
            return
        
        # Get selected A[] index
        selected = self.csv_array_combo.currentText()  # "A[0]", "A[1]", ...
        index = int(selected[2])  # Get number
        
        # Get value from A[]
        value = self.calc.A[index]
        
        if value is None:
            QMessageBox.warning(self, "Warning", f"A[{index}] is empty, please save value first")
            return
        
        # Addto CSV Data List
        self.csv_data.append((name, value))
        
        # clearEmptynameinputbox
        self.csv_name_input.clear()
        
        QMessageBox.information(self, "Success", 
            f"Added:\nName: {name}\nSource: A[{index}]\nValue: {value}")
    
    def on_reg_value_changed(self):
        """Register value changed,auto update decimal display"""
        if self.converting:
            return
        
        reg_text = self.reg_value_input.text().strip()
        
        if not reg_text or reg_text == '0x':
            return
        
        try:
            # ParseRegister value (Support 0x, 0b, Decimal)
            value = self.parse_value(reg_text)
            
            # Update10decimal display
            self.converting = True
            self.dec_display.setText(str(value))
            self.converting = False
            
        except (ValueError, Exception):
            # Input is not validnumber,clearEmpty10decimal display
            self.converting = True
            self.dec_display.setText("")
            self.converting = False
    
    def on_dec_display_changed(self):
        """10 decimal display changed,auto update register value"""
        if self.converting:
            return
        
        dec_text = self.dec_display.text().strip()
        
        if not dec_text:
            return
        
        try:
            # Convert to hexadecimal
            dec_value = int(dec_text)
            hex_value = hex(dec_value)  # 0xabcd format
            
            self.converting = True
            self.reg_value_input.setText(hex_value)
            self.converting = False
            
        except ValueError:
            pass