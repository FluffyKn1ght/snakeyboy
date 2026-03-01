class AddressBus:
    """PLACEHOLDER CLASS - TODO: Implement"""

    def read(self, address: int) -> int:
        return 0

    def readw(self, address: int) -> int:
        return 0

    def write(self, address: int, value: int) -> None:
        pass


class IllegalInstruction(Exception):
    """Exception that gets raised whenever an illegal CPU instruction is hit.

    Attributes:
        msg (str): Exception message
    """

    def __init__(self, msg: str, *args: object) -> None:
        """Creates a new IllegalInstruction exception

        Arguments:
            msg (str): Exception message
        """

        self.msg = msg
        super().__init__(*args)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.msg}"


class CPUFlags:
    """Provides a more concise way to represent CPU flags in the F register

    Values:
        - Z - Zero flag
        - N - Subtract flag
        - H - Half carry flag
        - C - Carry flag
    """

    Z = 0b10000000
    N = 0b01000000
    H = 0b00100000
    C = 0b00010000


class GameBoyCPU:
    """Represents the CPU of a Sharp LR35902 SoC from the classic DMG (Dot Matrix Game) GameBoy.

    Propeties:
        a, f, b, c, d, e, h, l (int) - Abstractions for 8-bit register access with overflow/underflow behaviour
        af, bc, de, hl (int) - Abstractions for 16-bit register access
        pc (int) - Abstraction for the program counter with overflow/underflow behaviour
        sp (int) - Abstraction for the stack pointer with overflow/underflow behaviour

    Attributes:
        ime (bool) - Interrupt master enable
    """

    def __init__(self) -> None:
        """Creates a blank CPU instance."""

        self._a = 0
        self._f = 0
        self._b = 0
        self._c = 0
        self._d = 0
        self._e = 0
        self._h = 0
        self._l = 0

        self._pc = 0
        self._sp = 0

        self.ime = False

    @property
    def pc(self) -> int:
        """Gets the current value of the program counter (PC)

        Returns:
            (int) The current value of the PC
        """

        return self._pc

    @pc.setter
    def pc(self, to: int) -> None:
        """Sets the current value of the program counter (PC)

        Arguments:
            - to (int) - The new value of the PC
        """

        while to < 0:
            to += 0xFFFF
        while to > 0xFFFF:
            to -= 0xFFFF

        self._pc = to

    @property
    def sp(self) -> int:
        """Gets the current value of the stack pointer (SP)

        Returns:
            (int) The current value of the SP
        """

        return self._sp

    @sp.setter
    def sp(self, to: int) -> None:
        """Sets the current value of the program counter (SP)

        Arguments:
            - to (int) - The new value of the SP
        """

        while to < 0:
            to += 0xFFFF
        while to > 0xFFFF:
            to -= 0xFFFF

        self._sp = to

    @property
    def a(self) -> int:
        """Gets the contents of the A register

        Returns:
            (int) The value of the A register
        """

        return self._a

    @a.setter
    def a(self, to: int) -> None:
        """Sets the contents of the A register to an 8-bit value, simulating overflow/underflow behaviour

        Arguments:
            - to (int): The new value of the A register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._a = to & 0xFF

    @property
    def f(self) -> int:
        """Gets the contents of the F register

        Returns:
            (int) The value of the F register
        """

        return self._f

    @f.setter
    def f(self, to: int) -> None:
        """Sets the contents of the F register to an 8-bit value, simulating overflow/underflow behaviour.
        The lower nibble is always zeroed out.

        Arguments:
            - to (int): The new value of the F register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._f = to & 0xF0

    @property
    def b(self) -> int:
        """Gets the contents of the B register

        Returns:
            (int) The value of the B register
        """

        return self._b

    @b.setter
    def b(self, to: int) -> None:
        """Sets the contents of the B register to an 8-bit value, simulating overflow/underflow behaviour.

        Arguments:
            - to (int): The new value of the B register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._b = to & 0xFF

    @property
    def c(self) -> int:
        """Gets the contents of the C register

        Returns:
            (int) The value of the C register
        """

        return self._c

    @c.setter
    def c(self, to: int) -> None:
        """Sets the contents of the C register to an 8-bit value, simulating overflow/underflow behaviour.

        Arguments:
            - to (int): The new value of the C register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._c = to & 0xFF

    @property
    def d(self) -> int:
        """Gets the contents of the D register

        Returns:
            (int) The value of the D register
        """

        return self._d

    @d.setter
    def d(self, to: int) -> None:
        """Sets the contents of the D register to an 8-bit value, simulating overflow/underflow behaviour.

        Arguments:
            - to (int): The new value of the D register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._d = to & 0xFF

    @property
    def e(self) -> int:
        """Gets the contents of the E register

        Returns:
            (int) The value of the E register
        """

        return self._e

    @e.setter
    def e(self, to: int) -> None:
        """Sets the contents of the E register to an 8-bit value, simulating overflow/underflow behaviour.

        Arguments:
            - to (int): The new value of the E register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._e = to & 0xFF

    @property
    def h(self) -> int:
        """Gets the contents of the H register

        Returns:
            (int) The value of the H register
        """

        return self._h

    @h.setter
    def h(self, to: int) -> None:
        """Sets the contents of the H register to an 8-bit value, simulating overflow/underflow behaviour.

        Arguments:
            to (int): The new value of the H register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._h = to & 0xFF

    @property
    def l(self) -> int:
        """Gets the contents of the C register

        Returns:
            (int) The value of the C register
        """

        return self._l

    @l.setter
    def l(self, to: int) -> None:
        """Sets the contents of the L register to an 8-bit value, simulating overflow/underflow behaviour.

        Arguments:
            to (int): The new value of the L register
        """

        while to < 0:
            to += 0xFF
        while to > 0xFF:
            to -= 0xFF

        self._l = to & 0xFF

    @property
    def af(self) -> int:
        """Gets the contents of registers A and F as one 16-bit value

        Returns:
            (int) The value of the AF register pair
        """

        return (self.a << 8) | self.f

    @af.setter
    def af(self, to: int) -> None:
        """(Setter method - use `self.de = ...` instead)

        Sets the contents of registers A and F based on a 16-bit value

        Arguments:
            - to (int): The new value of the AF register pair
        """

        self.a = (to & 0xFF00) >> 8
        self.f = to & 0xF0

    @property
    def bc(self) -> int:
        """Gets the contents of registers B and C as one 16-bit value

        Returns:
            (int) The value of the BC register pair
        """

        return (self.b << 8) | self.c

    @bc.setter
    def bc(self, to: int) -> None:
        """(Setter method - use `self.bc = ...` instead)

        Sets the contents of registers B and C based on a 16-bit value

        Arguments:
            - to (int): The new value of the BC register pair
        """

        self.b = (to & 0xFF00) >> 8
        self.c = to & 0xFF

    @property
    def de(self) -> int:
        """Gets the contents of registers D and E as one 16-bit value

        Returns:
            (int) The value of the DE register pair
        """

        return (self.d << 8) | self.e

    @de.setter
    def de(self, to: int) -> None:
        """(Setter method - use `self.de = ...` instead)

        Sets the contents of registers D and E based on a 16-bit value

        Arguments:
            - to (int): The new value of the DE register pair
        """

        self.d = (to & 0xFF00) >> 8
        self.e = to & 0xFF

    @property
    def hl(self) -> int:
        """Gets the contents of registers H and L as one 16-bit value

        Returns:
            (int) The value of the HL register pair
        """

        return (self.h << 8) | self.l

    @hl.setter
    def hl(self, to: int) -> None:
        """(Setter method - use `self.hl = ...` instead)

        Sets the contents of registers H and L based on a 16-bit value

        Arguments:
            - to (int): The new value of the HL register pair
        """

        self.h = (to & 0xFF00) >> 8
        self.l = to & 0xFF

    def _advance_pc(self) -> int:
        # Increments the PC and returns its previous value

        progcnt = self.pc
        self.pc += 1
        self.pc &= 0xFFFF
        return progcnt

    def _stack_push(self, addrbus: AddressBus, value: int) -> None:
        # Pushes a value onto the stack

        self.sp -= 1
        addrbus.write(self.sp, value & 0xFF)
        self.sp -= 1
        addrbus.write(self.sp, (value & 0xFF00) >> 8)

    def _stack_pop(self, addrbus: AddressBus) -> int:
        # Pops a value from the stack

        self.sp += 1
        value = addrbus.readw(self.sp)
        self.sp += 1
        return value

    def execute_instruction(self, addrbus: AddressBus) -> int:
        """Reads and executes a CPU instruction.

        Arguments:
            - addrbus (AddressBus): The address bus the CPU should use for reading/writing data

        Returns:
            (int) The amount of machine cycles (CPU cycles / 4) that the instruction took

        Raises:
            - IllegalInstruction - An unknown opcode was hit
        """

        opcode = addrbus.read(self._advance_pc())

        match opcode:
            case 0x06:  # ld imm8, b
                imm8 = addrbus.read(self._advance_pc())
                self.b = imm8
                return 2
            case 0x0E:  # ld imm8, c
                imm8 = addrbus.read(self._advance_pc())
                self.c = imm8
                return 2
            case 0x16:  # ld imm8, d
                imm8 = addrbus.read(self._advance_pc())
                self.d = imm8
                return 2
            case 0x1E:  # ld imm8, e
                imm8 = addrbus.read(self._advance_pc())
                self.e = imm8
                return 2
            case 0x26:  # ld imm8, h
                imm8 = addrbus.read(self._advance_pc())
                self.h = imm8
                return 2
            case 0x2E:  # ld imm8, l
                imm8 = addrbus.read(self._advance_pc())
                self.l = imm8
                return 2
            # =====================================================
            case 0x7F:  # ld a, a
                # NOTE: This is effectively a NOP
                self.a = self.a
                return 1
            case 0x78:  # ld a, b
                self.a = self.b
                return 1
            case 0x79:  # ld a, c
                self.a = self.c
                return 1
            case 0x7A:  # ld a, d
                self.a = self.d
                return 1
            case 0x7B:  # ld a, e
                self.a = self.e
                return 1
            case 0x7C:  # ld a, h
                self.a = self.h
                return 1
            case 0x7D:  # ld a, l
                self.a = self.l
                return 1
            case 0x7E:  # ld a, [hl]
                self.a = addrbus.read(self.hl)
                return 2
            case 0x0A:  # ld a, [bc]
                self.a = addrbus.read(self.bc)
                return 2
            case 0x1A:  # ld a, [de]
                self.a = addrbus.read(self.de)
                return 2
            case 0xFA:  # ld a, [imm16]
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                self.a = addrbus.read(imm16)
                return 4
            case 0x3E:  # ld a, [imm8]
                self.a = addrbus.read(self._advance_pc())
                return 2
            # =====================================================
            case 0x40:  # ld b, b
                # NOTE: This is effectively a NOP
                self.b = self.b
                return 1
            case 0x41:  # ld b, c
                self.b = self.c
                return 1
            case 0x42:  # ld b, d
                self.b = self.d
                return 1
            case 0x43:  # ld b, e
                self.b = self.e
                return 1
            case 0x44:  # ld b, h
                self.b = self.h
                return 1
            case 0x45:  # ld b, l
                self.b = self.l
                return 1
            case 0x46:  # ld b, [hl]
                self.b = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x48:  # ld c, b
                self.c = self.b
                return 1
            case 0x49:  # ld c, c
                # NOTE: This is effectively a NOP
                self.c = self.c
                return 1
            case 0x4A:  # ld c, d
                self.c = self.d
                return 1
            case 0x4B:  # ld c, e
                self.c = self.e
                return 1
            case 0x4C:  # ld c, h
                self.c = self.h
                return 1
            case 0x4D:  # ld c, l
                self.c = self.l
                return 1
            case 0x4E:  # ld c, [hl]
                self.c = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x48:  # ld c, b
                self.c = self.b
                return 1
            case 0x49:  # ld c, c
                # NOTE: This is effectively a NOP
                self.c = self.c
                return 1
            case 0x4A:  # ld c, d
                self.c = self.d
                return 1
            case 0x4B:  # ld c, e
                self.c = self.e
                return 1
            case 0x4C:  # ld c, h
                self.c = self.h
                return 1
            case 0x4D:  # ld c, l
                self.c = self.l
                return 1
            case 0x4E:  # ld c, [hl]
                self.c = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x50:  # ld d, b
                self.d = self.b
                return 1
            case 0x51:  # ld d, c
                self.d = self.c
                return 1
            case 0x52:  # ld d, d
                # NOTE: This is effectively a NOP
                self.d = self.d
                return 1
            case 0x53:  # ld d, e
                self.d = self.e
                return 1
            case 0x54:  # ld d, h
                self.d = self.h
                return 1
            case 0x55:  # ld d, l
                self.d = self.l
                return 1
            case 0x56:  # ld d, [hl]
                self.d = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x58:  # ld e, b
                self.e = self.b
                return 1
            case 0x59:  # ld e, c
                self.e = self.c
                return 1
            case 0x5A:  # ld e, d
                self.e = self.d
                return 1
            case 0x5B:  # ld e, e
                # NOTE: This is effectively a NOP
                self.e = self.e
                return 1
            case 0x5C:  # ld e, h
                self.e = self.h
                return 1
            case 0x5D:  # ld e, l
                self.e = self.l
                return 1
            case 0x5E:  # ld e, [hl]
                self.e = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x60:  # ld h, b
                self.h = self.b
                return 1
            case 0x61:  # ld h, c
                self.h = self.c
                return 1
            case 0x62:  # ld h, d
                self.h = self.d
                return 1
            case 0x63:  # ld h, e
                self.h = self.e
                return 1
            case 0x64:  # ld h, h
                # NOTE: This is effectively a NOP
                self.h = self.h
                return 1
            case 0x65:  # ld h, l
                self.h = self.l
                return 1
            case 0x66:  # ld h, [hl]
                self.h = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x68:  # ld l, b
                self.h = self.b
                return 1
            case 0x69:  # ld l, c
                # nice ;3
                self.h = self.c
                return 1
            case 0x6A:  # ld l, d
                self.h = self.d
                return 1
            case 0x6B:  # ld l, e
                self.h = self.e
                return 1
            case 0x6C:  # ld l, h
                self.h = self.h
                return 1
            case 0x6D:  # ld l, l
                # NOTE: This is effectively a NOP
                self.l = self.l
                return 1
            case 0x6E:  # ld l, [hl]
                self.l = addrbus.read(self.hl)
                return 2
            # =====================================================
            case 0x70:  # ld [hl], b
                addrbus.write(self.hl, self.b)
                return 2
            case 0x71:  # ld [hl], c
                addrbus.write(self.hl, self.c)
                return 2
            case 0x72:  # ld [hl], d
                addrbus.write(self.hl, self.d)
                return 2
            case 0x73:  # ld [hl], e
                addrbus.write(self.hl, self.e)
                return 2
            case 0x74:  # ld [hl], h
                addrbus.write(self.hl, self.h)
                return 2
            case 0x75:  # ld [hl], l
                addrbus.write(self.hl, self.h)
                return 2
            case 0x36:  # ld [hl], imm8
                imm8 = addrbus.read(self._advance_pc())
                addrbus.write(self.hl, imm8)
                return 3
            # =====================================================
            case 0x47:  # ld b, a
                self.b = self.a
                return 1
            case 0x4F:  # ld c, a
                self.c = self.a
                return 1
            case 0x57:  # ld d, a
                self.d = self.a
                return 1
            case 0x5F:  # ld e, a
                self.e = self.a
                return 1
            case 0x67:  # ld h, a
                self.h = self.a
                return 1
            case 0x6F:  # ld l, a
                self.l = self.a
                return 1
            case 0x02:  # ld [bc], a
                addrbus.write(self.bc, self.a)
                return 2
            case 0x12:  # ld [de], a
                addrbus.write(self.de, self.a)
                return 2
            case 0x77:  # ld [hl], a
                addrbus.write(self.hl, self.a)
                return 2
            case 0xEA:  # ld [imm16], a
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                addrbus.write(imm16, self.a)
                return 4
            # =====================================================
            case 0xF2:  # ld a, [$FF00+c]
                self.a = addrbus.read(0xFF00 + self.c)
                return 2
            case 0xE2:  # ld [$FF00+c], a
                addrbus.write(0xFF00 + self.c, self.a)
                return 2
            # =====================================================
            case 0x3A:  # ldd a, [hl]
                self.a = addrbus.read(self.hl)
                self.hl -= 1
                return 2
            case 0x32:  # ldd [hl], a
                addrbus.write(self.hl, self.a)
                self.hl -= 1
                return 2
            case 0x2A:  # ldi a, [hl]
                self.a = addrbus.read(self.hl)
                self.hl += 1
                return 2
            case 0x22:  # ldi [hl], a
                addrbus.write(self.hl, self.a)
                self.hl += 1
                return 2
            # =====================================================
            case 0xE0:  # ldh [$FF00+imm8], a
                imm8 = addrbus.read(self._advance_pc())
                addrbus.write(0xFF00 + imm8, self.a)
                return 3
            case 0xF0:  # ldh a, [$FF00+imm8]
                imm8 = addrbus.read(self._advance_pc())
                self.a = addrbus.read(0xFF00 + imm8)
                return 3
            # =====================================================
            case 0x01:  # ld bc, imm16
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                self.bc = imm16
                return 3
            case 0x11:  # ld de, imm16
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                self.de = imm16
                return 3
            case 0x21:  # ld hl, imm16
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                self.hl = imm16
                return 3
            case 0x31:  # ld sp, imm16
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                self.sp = imm16 & 0xFFFF
                return 3
            # =====================================================
            case 0xF9:  # ld sp, hl
                self.sp = self.hl
                return 2
            # =====================================================
            case 0xF8:  # ld hl, sp+imm8
                # TODO: figure H and C flags out
                imm8 = addrbus.read(self._advance_pc())
                self.hl = self.sp + imm8
                self.f &= CPUFlags.H | CPUFlags.C  # reset Z and N flags
                return 3
            # =====================================================
            case 0x08:  # ld [imm16], sp
                imm16 = addrbus.readw(self._advance_pc())
                self._advance_pc()
                addrbus.write(imm16, self.sp & 0xFF)
                addrbus.write(imm16 + 1, (self.sp & 0xFF00) >> 8)
                return 5
            # =====================================================
            case 0xF5:  # push af
                self._stack_push(addrbus, self.af)
                return 4
            case 0xC5:  # push bc
                self._stack_push(addrbus, self.bc)
                return 4
            case 0xD5:  # push de
                self._stack_push(addrbus, self.de)
                return 4
            case 0xE5:  # push hl
                self._stack_push(addrbus, self.hl)
                return 4
            case 0xF1:  # pop af
                self.af = self._stack_pop(addrbus)
            case 0xC1:  # pop bc
                self.bc = self._stack_pop(addrbus)
            case 0xD1:  # pop de
                self.de = self._stack_pop(addrbus)
            case 0xE1:  # pop hl
                self.hl = self._stack_pop(addrbus)
            # =====================================================
            case 0x87:  # add a
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.a & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.a
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x80:  # add b
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.b & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.b
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x81:  # add c
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.c & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.c
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x82:  # add d
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.d & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.d
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x83:  # add e
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.e & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.e
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x84:  # add h
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.h & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.h
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x85:  # add l
                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (self.l & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.l
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x86:  # add [hl]
                value = addrbus.read(self.hl)

                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (value & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + value
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 2
            case 0xC6:  # add imm8
                imm8 = addrbus.read(self._advance_pc())

                self.f = 0

                # Set half carry flag
                nibble_result = (self.a & 0xF) + (imm8 & 0xF)
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + imm8
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 2
            # =====================================================
            case 0x8F:  # adc a
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.a & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.a + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x88:  # adc b
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.b & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.b + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x89:  # adc c
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.c & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.c + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x8A:  # adc d
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.d & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.d + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x8B:  # adc e
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.e & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.e + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x8C:  # adc h
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.h & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.h + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x8D:  # adc l
                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (self.l & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + self.l + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 1
            case 0x8E:  # adc [hl]
                value = addrbus.read(self.hl)

                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (value & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + value + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 2
            case 0xCE:  # adc imm8
                imm8 = addrbus.read(self._advance_pc())

                self.f = 0

                # Set half carry flag
                nibble_result = (
                    (self.a & 0xF) + (imm8 & 0xF) + ((self.f & CPUFlags.C) >> 4)
                )
                if nibble_result >= 0x10:
                    self.f |= CPUFlags.H

                # Set carry flag
                byte_result = self.a + imm8 + ((self.f & CPUFlags.C) >> 4)
                if byte_result >= 0x100:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (byte_result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = byte_result & 0xFF
                return 2
            # =====================================================
            case 0x97:  # sub a
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                # H flag is set whenever a borrow from bit 3 to 4 occurs, which happens
                # if the lower nibble of A < the lower nibble of n.
                if (self.a & 0xF) < (self.a & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                # C flag is set whenever a borrow from bit 7 occurs (aka the value of A underflows),
                # which happens if A < n.
                if self.a < self.a:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.a) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.a) & 0xFF
                return 1
            case 0x90:  # sub b
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.b & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.b:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.b) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.b) & 0xFF
                return 1
            case 0x91:  # sub c
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.c & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.c:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.c) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.c) & 0xFF
                return 1
            case 0x92:  # sub d
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.d & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.d:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.d) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.d) & 0xFF
                return 1
            case 0x93:  # sub e
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.e & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.e:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.e) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.e) & 0xFF
                return 1
            case 0x94:  # sub h
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.h & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.h:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.h) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.h) & 0xFF
                return 1
            case 0x95:  # sub l
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.l & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.l:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.l) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - self.l) & 0xFF
                return 1
            case 0x96:  # sub [hl]
                value = addrbus.read(self.hl)

                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (value & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < value:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - value) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - value) & 0xFF
                return 2
            case 0xD6:  # sub imm8
                imm8 = addrbus.read(self._advance_pc())

                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (imm8 & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < imm8:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - imm8) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - imm8) & 0xFF
                return 2
            # =====================================================
            case 0x9F:  # sbc a
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.a + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.a + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.a + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.a + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x98:  # sbc b
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.b + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.b + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.b + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.b + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x99:  # sbc c
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.c + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.c + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.c + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.c + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x9A:  # sbc d
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.d + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.d + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.d + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.d + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x9B:  # sbc e
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.e + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.e + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.e + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.e + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x9C:  # sbc h
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.h + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.h + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.h + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.h + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x9D:  # sbc l
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((self.l + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (self.l + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (self.l + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (self.l + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 1
            case 0x9E:  # sbc [hl]
                value = addrbus.read(self.hl)

                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < ((value + ((self.f & CPUFlags.C) >> 4)) & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < (value + ((self.f & CPUFlags.C) >> 4)):
                    self.f |= CPUFlags.C

                # Set zero flag
                if (abs(self.a - (value + ((self.f & CPUFlags.C) >> 4))) & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.a = (self.a - (value + ((self.f & CPUFlags.C) >> 4))) & 0xFF
                return 2
            # NOTE: sbc imm8 does not exist
            # =====================================================

        raise IllegalInstruction(f"Unknown opcode {hex(opcode)} at {hex(self.pc)}")
