# ql800Printer.py - print label to QL800
# Handles one and two line labels.

class Printer:
    def __init__(self):

        self.top_margin = 6  # The label is not under these dots
        self.top_indent = 5  # Arbitrary white space
        self.scale = 8  # Each font pixel has this many dots (300 DPI)
        self.line_space = 24  # Arbitrary but ~3 font pixels
        self.charIndex = 0
        self.pixelIndex = 0
        self.qty_labels_printed = 0
        self.columnCount = 0
        self.line = PrintHead()

        invalid = bytearray()
        for i in range(400):
            invalid.append(0x00)

        init = bytes([0x1b, 0x40])
        raster = bytes([0x1b, 0x69, 0x61, 0x01])
        status_dont = bytes([0x1b, 0x69, 0x21, 0x01])
        print_info = bytes([0x1b, 0x69, 0x7a, 0x8e, 0x0b, 0x1d, 0x5a, 0xdf, 0x03, 0x00, 0x00, 0x00, 0x00])
        auto_cut = bytes([0x1b, 0x69, 0x4d, 0x00])  # 0x40=auto cut, using NO CUT
        cut_each = bytes([0x1b, 0x69, 0x41, 0x01])
        expanded_mode = bytes([0x1b, 0x69, 0x4b, 0x00])  # 0x08=cut at end, 0x80=600DPI, using don't cut & 300DPI
        margin = bytes([0x1b, 0x69, 0x64, 0x00, 0x00])
        no_compression = bytes([0x4d, 0x00])

        self.blank_column = bytes([0x67, 0x00, 0x5a,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 1
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 2
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 3
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 4
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 5
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 6
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 7
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,   # 8
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # 9
        self.print_intermediate_label = bytes([0x0c])  # End of raster data for all but the last label
        self.print_last_label = bytes([0x1a])  # Ends raster data for last label

        self.prelabel = bytearray()
        self.prelabel.extend(invalid)
        self.prelabel.extend(init)
        self.prelabel.extend(raster)
        self.prelabel.extend(status_dont)
        self.prelabel.extend(print_info)
        self.prelabel.extend(auto_cut)
        self.prelabel.extend(cut_each)
        self.prelabel.extend(expanded_mode)
        self.prelabel.extend(margin)
        self.prelabel.extend(no_compression)

        self.prep = bytes([0x1b, 0x40, 0x1b, 0x69, 0x53])
        self.numerics = bytes([
            0x1f, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1f,  # 0
            0x1c, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1f,  # 1
            0x1f, 0x11, 0x01, 0x01, 0x1f, 0x10, 0x10, 0x10, 0x1f,  # 2
            0x1f, 0x11, 0x01, 0x01, 0x07, 0x01, 0x01, 0x11, 0x1f,  # 3
            0x11, 0x11, 0x11, 0x11, 0x1f, 0x01, 0x01, 0x01, 0x01,  # 4
            0x1f, 0x10, 0x10, 0x10, 0x1f, 0x01, 0x01, 0x11, 0x1f,  # 5
            0x1f, 0x11, 0x10, 0x10, 0x1f, 0x11, 0x11, 0x11, 0x1f,  # 6
            0x1f, 0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10, 0x10,  # 7
            0x1f, 0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11, 0x1f,  # 8
            0x1f, 0x11, 0x11, 0x11, 0x1f, 0x01, 0x01, 0x11, 0x1f,  # 9
        ])
        self.aToZ = bytes([
            0x0e, 0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11, 0x11,  # A
            0x1e, 0x11, 0x11, 0x11, 0x1e, 0x11, 0x11, 0x11, 0x1e,  # B
            0x0e, 0x11, 0x11, 0x10, 0x10, 0x10, 0x11, 0x11, 0x0e,  # C
            0x1e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1e,  # D
            0x1f, 0x10, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x10, 0x1f,  # E
            0x1f, 0x10, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x10, 0x10,  # F
            0x0e, 0x11, 0x10, 0x10, 0x10, 0x13, 0x11, 0x11, 0x0e,  # G
            0x11, 0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11, 0x11,  # H
            0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1f,  # I
            0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x11, 0x1e,  # J
            0x11, 0x11, 0x12, 0x14, 0x1c, 0x14, 0x12, 0x11, 0x11,  # K
            0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f,  # L
            0x11, 0x1b, 0x15, 0x15, 0x15, 0x11, 0x11, 0x11, 0x11,  # M
            0x11, 0x19, 0x19, 0x15, 0x15, 0x15, 0x13, 0x13, 0x11,  # N
            0x0e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e,  # O
            0x1e, 0x11, 0x11, 0x11, 0x1e, 0x10, 0x10, 0x10, 0x10,  # P
            0x0e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0e,  # Q
            0x1e, 0x11, 0x11, 0x11, 0x1e, 0x14, 0x12, 0x11, 0x11,  # R
            0x0e, 0x11, 0x10, 0x10, 0x0e, 0x01, 0x01, 0x11, 0x0e,  # S
            0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,  # T
            0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e,  # U
            0x11, 0x11, 0x11, 0x11, 0x1b, 0x0a, 0x0a, 0x04, 0x04,  # V
            0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x15, 0x15, 0x0e,  # W
            0x11, 0x0a, 0x0a, 0x04, 0x04, 0x04, 0x0a, 0x0a, 0x11,  # X
            0x11, 0x0a, 0x0a, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,  # Y
            0x1f, 0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10, 0x1f,  # Z
        ])
        self.slash = bytes([
            0x01, 0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10, 0x10,  # /
        ])
        self.blank = bytes([
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # blank
        ])

    def print_label_one_line(self, text, copies):
        self.charIndex = 0
        self.pixelIndex = 0

        printer = "/dev/usb/lp0"
        ptr = open(printer, "r+b")
        ptr.write(self.prep)
        #  status = ptr.read(32)  #  Previously was this now just read
        ptr.read(32)
        ptr.write(self.prelabel)

        self.qty_labels_printed = 0

        text = text.upper()  # Have uppercase font

        while True:
            # Print one copy
            # insert one blank column to left of text
            ptr.write(self.blank_column)
            self.columnCount = 1

            for c in text:
                # Print each char
                # Form a printhead column of data for each font pixel.
                # Five columns of 9 pixels
                for self.pixelIndex in range(5):
                    self.form_column_one_line(c)
                    # Repeat that column 'scale' times
                    for s in range(self.scale):
                        ptr.write(self.line.data)
                        self.columnCount += 1
                # inter-character spacing - a little wider than a pixel.
                for spacing in range(int(self.scale * 1.5)):
                    ptr.write(self.blank_column)
                    self.columnCount += 1
            # Fill remainder of label with blank_column
            blank_qty = 991 - self.columnCount
            for blank_line_count in range(blank_qty):
                ptr.write(self.blank_column)
            # End this copy
            self.qty_labels_printed += 1
            if self.qty_labels_printed < copies:
                ptr.write(self.print_intermediate_label)
            else:
                break
            pass

        ptr.write(self.print_last_label)
        ptr.close()

    def form_column_one_line(self, character):
        self.line = PrintHead()
        self.line.insert_white_pixels(self.top_margin)
        self.line.insert_white_pixels(self.top_indent)
        if character == '/':
            self.line.insert_font_char(self.slash, 0, self.pixelIndex, self.scale)
            self.line.fill_to_end()
            return

        if '0' <= character <= '9':
            # Is numeric
            font_index = ord(character) - ord('0')
            self.line.insert_font_char(self.numerics, font_index, self.pixelIndex, self.scale)
            self.line.fill_to_end()
            return

        if 'A' <= character <= 'Z':
            # Is numeric
            font_index = ord(character) - ord('A')
            self.line.insert_font_char(self.aToZ, font_index, self.pixelIndex, self.scale)
            self.line.fill_to_end()
            return

        # Unknown character
        self.line.fill_to_end()
        return

    def print_label_two_lines(self, text1, text2, copies):
        self.charIndex = 0
        self.pixelIndex = 0

        printer = "/dev/usb/lp0"
        ptr = open(printer, "r+b")
        ptr.write(self.prep)
        # status = ptr.read(32)  #  Previously was this now just read
        ptr.read(32)
        ptr.write(self.prelabel)

        text1 = text1.upper()
        text2 = text2.upper()

        char_count = len(text1)
        if char_count > len(text2):
            # Append blanks to text 2 to make same length
            pad = char_count - len(text2)
            text2 = text2 + ' ' * pad
        else:
            # Text 2 is longer, pad text 1
            char_count = len(text2)
            pad = char_count - len(text1)
            text1 = text1 + ' ' * pad

        self.qty_labels_printed = 0

        while True:
            # Print one copy
            # insert one blank column to left of text - Why? Just do.
            ptr.write(self.blank_column)
            self.columnCount = 1

            for i in range(char_count):
                # Print each char
                # Form a printhead column of data for each font pixel.
                # Five columns of 9 pixels
                c1 = text1[i]
                c2 = text2[i]
                for self.pixelIndex in range(5):
                    self.form_column_two_lines(c1, c2)
                    # Repeat that column 'scale' times
                    for s in range(self.scale):
                        ptr.write(self.line.data)
                        self.columnCount += 1
                # inter-character spacing - a little wider than a pixel.
                for spacing in range(int(self.scale * 1.5)):
                    ptr.write(self.blank_column)
                    self.columnCount += 1

            # Fill remainder of label with blank_column
            blank_qty = 991 - self.columnCount
            for blank_line_count in range(blank_qty):
                ptr.write(self.blank_column)
            # End this copy
            self.qty_labels_printed += 1
            if self.qty_labels_printed < copies:
                ptr.write(self.print_intermediate_label)
            else:
                break
            pass

        ptr.write(self.print_last_label)
        ptr.close()

    def form_column_two_lines(self, char1, char2):
        self.line = PrintHead()
        self.line.insert_white_pixels(self.top_margin)
        self.line.insert_white_pixels(self.top_indent)

        if char1 == '/':
            self.line.insert_font_char(self.slash, 0, self.pixelIndex, self.scale)
        elif '0' <= char1 <= '9':
            # Is numeric
            font_index = ord(char1) - ord('0')
            self.line.insert_font_char(self.numerics, font_index, self.pixelIndex, self.scale)
        elif 'A' <= char1 <= 'Z':
            # Is numeric
            font_index = ord(char1) - ord('A')
            self.line.insert_font_char(self.aToZ, font_index, self.pixelIndex, self.scale)
        else:
            # Unknown character - insert blank
            self.line.insert_font_char(self.blank, 0, self.pixelIndex, self.scale)

        # Space between lines
        self.line.insert_white_pixels(self.line_space)

        if char2 == '/':
            self.line.insert_font_char(self.slash, 0, self.pixelIndex, self.scale)
        elif '0' <= char2 <= '9':
            # Is numeric
            font_index = ord(char2) - ord('0')
            self.line.insert_font_char(self.numerics, font_index, self.pixelIndex, self.scale)
        elif 'A' <= char2 <= 'Z':
            # Is numeric
            font_index = ord(char2) - ord('A')
            self.line.insert_font_char(self.aToZ, font_index, self.pixelIndex, self.scale)
        else:
            # Unknown character
            self.line.insert_font_char(self.blank, 0, self.pixelIndex, self.scale)

        # Fill out the column
        self.line.fill_to_end()


class PrintHead:
    # Font is 9x5
    # The print head needs 720 bits of data + plus 3 preamble bytes.
    def __init__(self):
        self.data = bytearray()
        preamble = bytes([0x67, 0x00, 0x5a])
        self.data.extend(preamble)
        self.thisByte = bytearray(1)
        self.mask = 0x80
        self.byteQty = 0
        self.bitQty = 0

    def insert_pixel(self, dark):
        if dark:
            self.thisByte[0] |= self.mask
        self.mask = self.mask >> 1
        self.bitQty += 1
        if self.mask == 0:
            self.mask = 0x80
            self.data.append(self.thisByte[0])
            self.byteQty += 1
            self.bitQty = 0
            self.thisByte[0] &= 0x00

    def insert_white_pixels(self, qty):
        for i in range(qty):
            self.insert_pixel(False)

    def insert_dark_pixels(self, qty):
        for i in range(qty):
            self.insert_pixel(True)

    def fill_to_end(self):
        # Calc remaining pixels.
        # Print head has 720 pixels
        qty = (90 * 8) - (8 * self.byteQty) - self.bitQty
        self.insert_white_pixels(qty)

    def insert_font_char(self, font_bytes, font_char_index, pixel_index, scale):
        mask = 0x10 >> pixel_index
        first_vertical_pixel = (font_char_index * 9)  # nine bytes per char
        for vertPixel in range(9):
            if font_bytes[first_vertical_pixel] & mask:
                self.insert_dark_pixels(scale)
            else:
                self.insert_white_pixels(scale)
            first_vertical_pixel += 1
