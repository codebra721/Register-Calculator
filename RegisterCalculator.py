import math

class RegisterCalculator:
    def __init__(self):
        # Storage arrays
        self.A = [None] * 10  # Value array
        self.F = [None] * 10  # Formula array
        self.R = [None] * 10  # Register raw value array
        
    def extract_bits(self, value, start_bit, end_bit):
        """
        Extract bit range
        value: Register value
        start_bit: Start bit (LSB)
        end_bit: End bit (MSB)
        """
        if start_bit > end_bit:
            raise ValueError("Start bitcannot be greater thanEnd bit")
        
        # Calculate number of bits
        num_bits = end_bit - start_bit + 1
        
        # Create mask
        mask = (1 << num_bits) - 1
        
        # Extract Bits
        extracted = (value >> start_bit) & mask
        
        return extracted
    
    def store_value(self, array_name, index, value):
        """Store value to specified array"""
        if array_name == 'A':
            self.A[index] = value
        elif array_name == 'F':
            self.F[index] = value
        elif array_name == 'R':
            self.R[index] = value
    
    def get_array(self, array_name):
        """Get array content"""
        if array_name == 'A':
            return self.A
        elif array_name == 'F':
            return self.F
        elif array_name == 'R':
            return self.R
    
    def calculate_formula(self, formula, v=None):
        """
        Calculate Formula
        formula: Formula string (can contain A[n], bit_val and other variables)
        bit_val: Current bit extraction value (Optional)
        """
        
        # Create safe namespace
        safe_dict = {
            # Value array
            'a0': self.A[0] if self.A[0] is not None else 0,
            'a1': self.A[1] if self.A[1] is not None else 0,
            'a2': self.A[2] if self.A[2] is not None else 0,
            'a3': self.A[3] if self.A[3] is not None else 0,
            'a4': self.A[4] if self.A[4] is not None else 0,
            'a5': self.A[5] if self.A[5] is not None else 0,
            'a6': self.A[6] if self.A[6] is not None else 0,
            'a7': self.A[7] if self.A[7] is not None else 0,
            'a8': self.A[8] if self.A[8] is not None else 0,
            'a9': self.A[9] if self.A[9] is not None else 0,
            # Formula array
            'f0': self.F[0] if self.F[0] is not None else 0,
            'f1': self.F[1] if self.F[1] is not None else 0,
            'f2': self.F[2] if self.F[2] is not None else 0,
            'f3': self.F[3] if self.F[3] is not None else 0,
            'f4': self.F[4] if self.F[4] is not None else 0,
            'f5': self.F[5] if self.F[5] is not None else 0,
            'f6': self.F[6] if self.F[6] is not None else 0,
            'f7': self.F[7] if self.F[7] is not None else 0,
            'f8': self.F[8] if self.F[8] is not None else 0,
            'f9': self.F[9] if self.F[9] is not None else 0,
            'v': v,
            # Math functions
            'abs': abs,
            'round': round,
            'pow': pow,
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            # Constants
            'pi': math.pi,
            'e': math.e,
        }
        
        try:
            # Use eval Calculate Formula
            result = eval(formula, {"__builtins__": {}}, safe_dict)
            return result
        except Exception as e:
            raise ValueError(f"Formula calculation error: {e}")