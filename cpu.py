import struct
from typing import Tuple


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


class ArmState:
    """Contains representations for all possible states of instructions that require arming (take effect only after the next instruction).
    (Example: halt, stop, ei/di)

    Values:
        - NOT_ARMED - Not halted/stopped (or doesn't matter), and not armed
        - ARMED - Not halted/stopped (or doesn't matter), but armed
        - ACTIVE - Halted/stopped
    """

    NOT_ARMED = 0
    ARMED = 1
    ACTIVE = 2


class GameBoyCPU:
    """Represents the CPU of a Sharp LR35902 SoC from the classic DMG (Dot Matrix Game) GameBoy.

    Propeties:
        a, f, b, c, d, e, h, l (int) - Abstractions for 8-bit register access with overflow/underflow behaviour
        af, bc, de, hl (int) - Abstractions for 16-bit register access
        pc (int) - Abstraction for the program counter with overflow/underflow behaviour
        sp (int) - Abstraction for the stack pointer with overflow/underflow behaviour
        halted, stopped, ei_armed, di_armed (bool) - Abstractions for halt (wait until interrupt)/stop (ultra-low-power mode) states, as well as ei/di instruction states
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

        self._halt_state = ArmState.NOT_ARMED
        self._stop_state = ArmState.NOT_ARMED
        self._ei_state = ArmState.NOT_ARMED
        self._di_state = ArmState.NOT_ARMED

        self._ime = False

    @staticmethod
    def _rotate_left_8(value: int) -> Tuple[int, int]:
        # Performs an 8-bit bit rotation to the left on the provided value
        shifted = value << 1
        old_edge_bit = (shifted & 0x100) >> 8

        return ((shifted & 0xFF) | old_edge_bit, old_edge_bit)

    @staticmethod
    def _rotate_right_8(value: int) -> Tuple[int, int]:
        # Performs an 8-bit bit rotation to the right on the provided value
        old_edge_bit = value & 0b1
        shifted = value >> 1

        return (shifted | (old_edge_bit << 7), old_edge_bit)

    @staticmethod
    def _rotate_left_9(value: int) -> Tuple[int, int]:
        # Performs a 9-bit bit rotation to the left on the provided value
        shifted = value << 1
        old_edge_bit = (shifted & 0x200) >> 9

        return ((shifted & 0x1FF) | old_edge_bit, old_edge_bit)

    @staticmethod
    def _rotate_right_9(value: int) -> Tuple[int, int]:
        # Performs a 9-bit bit rotation to the right on the provided value
        old_edge_bit = value & 0b1
        shifted = value >> 1

        return (shifted | (old_edge_bit << 8), old_edge_bit)

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

        to &= 0xFFFF
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

        to &= 0xFFFF
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

        to &= 0xFFFF
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

        to &= 0xFFFF
        self.h = (to & 0xFF00) >> 8
        self.l = to & 0xFF

    @property
    def halted(self) -> bool:
        """Gets the current halt status of the CPU - `True` if it's halted (waiting for an interrupt) and `False` otherwise.

        Setting this property to `True` will arm the halt state - the CPU will halt after running the next instruction.
        Setting this property to `False` will immidiately end the halt state.

        Returns:
            (bool) Whether the CPU is currently halted or not
        """

        return self._halt_state == ArmState.ACTIVE

    @halted.setter
    def halted(self, to: bool) -> None:
        """(Setter method - use `self.halted = ...` instead)

        Arms the halt state of the CPU if `to` is `True`, ends the halt state if it's `False`.

        Arguments:
            - to (int): Whether to arm the halt state or to end it
        """

        if to:
            if self._halt_state == ArmState.NOT_ARMED:
                self._halt_state = ArmState.ARMED
        else:
            self._halt_state = ArmState.NOT_ARMED

    @property
    def stopped(self) -> bool:
        """Gets the current stop status of the CPU - `True` if it's stopped (ultra-low-power mode) and `False` otherwise.

        Setting this property to `True` will arm the stop state - the CPU will stop after running the next instruction.
        Setting this property to `False` will immidiately end the stop state.

        Returns:
            (bool) Whether the CPU is currently halted or not
        """

        return self._stop_state == ArmState.ACTIVE

    @stopped.setter
    def stopped(self, to: bool) -> None:
        """(Setter method - use `self.stopped = ...` instead)

        Arms the stop state of the CPU if `to` is `True`, ends the stop state if it's `False`.

        Arguments:
            - to (int): Whether to arm the stop state or to end it
        """

        if to:
            if self._stop_state == ArmState.NOT_ARMED:
                self._stop_state = ArmState.ARMED
        else:
            self._stop_state = ArmState.NOT_ARMED

    @property
    def ei_armed(self) -> bool:
        """Gets the current armed status of the EI instruction - `True` if IME will be **enabled** after executing the next instruction, `False` otherwise.

        Setting this property to `True` will arm IME to be enabled after the next instruction, *if* the IME is currently disabled.
        Setting this property to `False` has no effect.

        Returns:
            (bool) The armed status of the EI instruction
        """

        return self._ei_state == ArmState.ARMED

    @ei_armed.setter
    def ei_armed(self, to: bool) -> None:
        """(Setter method - use `self.ei_armed = ...` instead)

        Arms the IME to be **enabled** after the next instruction is executed if `to` is `True`.

        Attributes:
            - to (bool): Must be `True` to arm, otherwise no effect
        """

        if to:
            if not self._ime:
                if self._ei_state == ArmState.NOT_ARMED:
                    self._ei_state = ArmState.ARMED

    @property
    def di_armed(self) -> bool:
        """Gets the current armed status of the DI instruction - `True` if IME will be **disabled** after executing the next instruction, `False` otherwise.

        Setting this property to `True` will arm IME to be disabled after the next instruction, *if* the IME is currently enabled.
        Setting this property to `False` has no effect.

        Returns:
            (bool) The armed status of the DI instruction
        """

        return self._ei_state == ArmState.ARMED

    @di_armed.setter
    def di_armed(self, to: bool) -> None:
        """(Setter method - use `self.di_armed = ...` instead)

        Arms the IME to be **enabled** after the next instruction is executed if `to` is `True`.

        Attributes:
            - to (bool): Must be `True` to arm, otherwise no effect
        """

        if to:
            if not self._ime:
                if self._di_state == ArmState.NOT_ARMED:
                    self._di_state = ArmState.ARMED

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

    def _get_n_and_carry_as_9bit(self, n: int) -> int:
        # Returns a 9-bit integer in the format of cnnnnnnnn
        carry_bit = (self.f | CPUFlags.C) >> 4
        return (carry_bit << 8) | n

    def _get_carry_and_n_as_9bit(self, n: int) -> int:
        # Returns a 9-bit integer in the format of nnnnnnnnc
        carry_bit = (self.f | CPUFlags.C) >> 4
        return (n << 1) | carry_bit

    def execute_instruction(self, addrbus: AddressBus) -> int:
        """Reads and executes a CPU instruction.

        Arguments:
            - addrbus (AddressBus): The address bus the CPU should use for reading/writing data

        Returns:
            (int) The amount of machine cycles (CPU cycles / 4) that the instruction took

        Raises:
            - IllegalInstruction - An unknown opcode was hit
        """

        # TODO: Handle armed stuff (halt/stop/ei/di)

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
            case 0xA7:  # and a
                self.f = CPUFlags.H

                if (self.a & self.a) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.a

                return 1
            case 0xA0:  # and b
                self.f = CPUFlags.H

                if (self.a & self.b) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.b

                return 1
            case 0xA1:  # and c
                self.f = CPUFlags.H

                if (self.a & self.c) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.c

                return 1
            case 0xA2:  # and d
                self.f = CPUFlags.H

                if (self.a & self.d) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.d

                return 1
            case 0xA3:  # and e
                self.f = CPUFlags.H

                if (self.a & self.e) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.e

                return 1
            case 0xA4:  # and h
                self.f = CPUFlags.H

                if (self.a & self.h) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.h

                return 1
            case 0xA5:  # and l
                self.f = CPUFlags.H

                if (self.a & self.l) == 0:
                    self.f |= CPUFlags.Z

                self.a &= self.l

                return 1
            case 0xA6:  # and [hl]
                value = addrbus.read(self.hl)

                self.f = CPUFlags.H

                if (self.a & value) == 0:
                    self.f |= CPUFlags.Z

                self.a &= value

                return 2
            case 0xE6:  # and imm8
                imm8 = addrbus.read(self._advance_pc())

                self.f = CPUFlags.H

                if (self.a & imm8) == 0:
                    self.f |= CPUFlags.Z

                self.a &= imm8

                return 2
            # =====================================================
            case 0xB7:  # or a
                self.f = 0

                if (self.a | self.a) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.a

                return 1
            case 0xB0:  # or b
                self.f = 0

                if (self.a | self.b) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.b

                return 1
            case 0xB1:  # or c
                self.f = 0

                if (self.a | self.c) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.c

                return 1
            case 0xB2:  # or d
                self.f = 0

                if (self.a | self.d) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.d

                return 1
            case 0xB3:  # or e
                self.f = 0

                if (self.a | self.e) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.e

                return 1
            case 0xB4:  # or h
                self.f = 0

                if (self.a | self.h) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.h

                return 1
            case 0xB5:  # or l
                self.f = 0

                if (self.a | self.l) == 0:
                    self.f |= CPUFlags.Z

                self.a |= self.l

                return 1
            case 0xB6:  # or [hl]
                value = addrbus.read(self.hl)

                self.f = 0

                if (self.a | value) == 0:
                    self.f |= CPUFlags.Z

                self.a |= value

                return 2
            case 0xF6:  # or imm8
                imm8 = addrbus.read(self._advance_pc())

                self.f = 0

                if (self.a | imm8) == 0:
                    self.f |= CPUFlags.Z

                self.a |= imm8

                return 2
            # =====================================================
            case 0xAF:  # xor a
                self.f = 0

                if (self.a ^ self.a) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.a

                return 1
            case 0xA8:  # xor b
                self.f = 0

                if (self.a ^ self.b) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.b

                return 1
            case 0xA9:  # xor c
                self.f = 0

                if (self.a ^ self.c) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.c

                return 1
            case 0xAA:  # xor d
                self.f = 0

                if (self.a ^ self.d) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.d

                return 1
            case 0xAB:  # xor e
                self.f = 0

                if (self.a ^ self.e) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.e

                return 1
            case 0xAC:  # xor h
                self.f = 0

                if (self.a ^ self.h) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.h

                return 1
            case 0xAD:  # xor l
                self.f = 0

                if (self.a ^ self.l) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= self.l

                return 1
            case 0xAE:  # xor [hl]
                value = addrbus.read(self.hl)

                self.f = 0

                if (self.a ^ value) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= value

                return 2
            case 0xEE:  # xor imm8
                imm8 = addrbus.read(self._advance_pc())

                self.f = 0

                if (self.a ^ imm8) == 0:
                    self.f |= CPUFlags.Z

                self.a ^= imm8

                return 2
            # =====================================================
            case 0xBF:  # cp a
                # N flag is always set as we're subtracting
                self.f = CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) < (self.a & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if self.a < self.a:
                    self.f |= CPUFlags.C

                # Set zero flag
                if (self.a - self.a) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                return 1
            case 0xB8:  # cp b
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

                return 1
            case 0xB9:  # cp c
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

                return 1
            case 0xBA:  # cp d
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

                return 1
            case 0xBB:  # cp e
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

                return 1
            case 0xBC:  # cp h
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
            case 0xBD:  # cp l
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

                return 1
            case 0xBE:  # cp [hl]
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

                return 2
            case 0xFE:  # cp imm8
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

                return 2
            # =====================================================
            case 0x3C:  # inc a
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.a & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.a + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a += 1
                return 1
            case 0x04:  # inc b
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.b & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.b + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.b += 1
                return 1
            case 0x0C:  # inc c
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.c & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.c + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.c += 1
                return 1
            case 0x14:  # inc d
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.d & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.d + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.d += 1
                return 1
            case 0x1C:  # inc e
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.e & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.e + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.e += 1
                return 1
            case 0x24:  # inc h
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.h & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.h + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.h += 1
                return 1
            case 0x2C:  # inc l
                self.f &= CPUFlags.C

                # Set half carry flag
                if (self.l & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.l + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.l += 1
                return 1
            case 0x34:  # inc [hl]
                value = addrbus.read(self.hl)

                self.f &= CPUFlags.C

                # Set half carry flag
                if (value & 0xF) + 1 > 0xFF:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (value + 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                value += 1
                addrbus.write(self.hl, value)
                return 3
            # =====================================================
            case 0x3D:  # dec a
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.a & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.a - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.a -= 1
                return 1
            case 0x05:  # dec b
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.b & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.b - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.b -= 1
                return 1
            case 0x0D:  # dec c
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.c & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.c - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.c -= 1
                return 1
            case 0x15:  # dec d
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.d & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.d - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.d -= 1
                return 1
            case 0x1D:  # dec e
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.e & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.e - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.e -= 1
                return 1
            case 0x25:  # dec h
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.h & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.h - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.h -= 1
                return 1
            case 0x2D:  # dec l
                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (self.l & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (self.l - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                self.l -= 1
                return 1
            case 0x35:  # inc [hl]
                value = addrbus.read(self.hl)

                self.f &= CPUFlags.C
                self.f |= CPUFlags.N

                # Set half carry flag
                if (value & 0xF) == 0:
                    self.f |= CPUFlags.H

                # Set zero flag
                if (value - 1) & 0xFF == 0:
                    self.f |= CPUFlags.Z

                value -= 1
                addrbus.write(self.hl, value)
                return 3
            # =====================================================
            case 0x09:  # add hl, bc
                self.f &= CPUFlags.Z

                # Set half carry flag
                if ((self.hl & 0xFFF) + (self.bc & 0xFFF)) > 0xFFF:
                    self.f |= CPUFlags.H

                # Set carry flag
                if (self.hl + self.bc) > 0xFFFF:
                    self.f |= CPUFlags.C

                self.hl += self.bc
                return 2
            case 0x19:  # add hl, de
                self.f &= CPUFlags.Z

                # Set half carry flag
                if ((self.hl & 0xFFF) + (self.de & 0xFFF)) > 0xFFF:
                    self.f |= CPUFlags.H

                # Set carry flag
                if (self.hl + self.de) > 0xFFFF:
                    self.f |= CPUFlags.C

                self.hl += self.de
                return 2
            case 0x29:  # add hl, hl
                self.f &= CPUFlags.Z

                # Set half carry flag
                if ((self.hl & 0xFFF) + (self.hl & 0xFFF)) > 0xFFF:
                    self.f |= CPUFlags.H

                # Set carry flag
                if (self.hl + self.hl) > 0xFFFF:
                    self.f |= CPUFlags.C

                self.hl += self.hl
                return 2
            case 0x09:  # add hl, sp
                self.f &= CPUFlags.Z

                # Set half carry flag
                if ((self.hl & 0xFFF) + (self.sp & 0xFFF)) > 0xFFF:
                    self.f |= CPUFlags.H

                # Set carry flag
                if (self.hl + self.sp) > 0xFFFF:
                    self.f |= CPUFlags.C

                self.hl += self.sp
                return 2
            # =====================================================
            case 0xE8:  # add sp, imm8s
                # NOTE: second operand (imm8s) is SIGNED - -127 to +127
                imm8s = addrbus.read(self._advance_pc())
                imm8s = struct.unpack("b", bytes([imm8s]))[0]

                # Set half carry flag
                if ((imm8s + self.sp) & 0xF) < (self.sp & 0xF):
                    self.f |= CPUFlags.H

                # Set carry flag
                if ((imm8s + self.sp) & 0xFF) < (self.sp & 0xFF):
                    self.f |= CPUFlags.C

                self.sp += imm8s

                return 4
            # =====================================================
            case 0x03:  # inc bc
                self.bc += 1

                return 2
            case 0x13:  # inc de
                self.de += 1

                return 2
            case 0x23:  # inc hl
                self.hl += 1

                return 2
            case 0x33:  # inc sp
                self.sp += 1

                return 2
            # =====================================================
            case 0x0B:  # dec bc
                self.bc -= 1

                return 2
            case 0x1B:  # dec de
                self.de -= 1

                return 2
            case 0x2B:  # dec hl
                self.hl -= 1

                return 2
            case 0x3B:  # dec sp
                self.sp -= 1

                return 2
            # =====================================================
            case 0x27:  # daa
                adjust = 0
                carry = 0

                # Decimal adjust register A after an ALU operation involving BCD numbers.
                if not (self.f & CPUFlags.N):
                    # Addition
                    lower_nibble = self.a & 0xF
                    if (self.f & CPUFlags.H) or (lower_nibble > 9):
                        adjust += 0x06

                    upper_nibble = (self.a & 0xF0) >> 4
                    if (self.f & CPUFlags.C) or (upper_nibble > 9):
                        adjust += 0x60
                        carry = CPUFlags.C
                else:
                    # Subtraction
                    if self.f & CPUFlags.H:
                        adjust -= 0x06

                    if self.c & CPUFlags.C:
                        adjust -= 0x60

                result = self.a + adjust

                if result > 0xFF:
                    result &= 0xFF
                    carry = CPUFlags.C

                self.a = result

                self.f &= CPUFlags.N

                if (result & 0xFF) == 0:
                    self.f |= CPUFlags.Z

                self.f |= CPUFlags.C & carry

                return 1
            # =====================================================
            case 0x2F:  # cpl
                self.a = ~self.a
                return 1
            # =====================================================
            case 0x3F:  # ccf
                carry = self.f & CPUFlags.C
                self.f &= CPUFlags.Z
                self.f |= ~carry & CPUFlags.C
                return 1
            # =====================================================
            case 0x37:  # scf
                self.f &= CPUFlags.Z
                self.f |= CPUFlags.C
                return 1
            # =====================================================
            case 0x00:  # nop
                # *insert carefree fox noises*
                return 1
            case 0x76:  # halt
                # *insert tired fox noises*
                self.halted = True
                return 1
            case 0x10:  # stop
                # *insert sleeping fox noises*
                self.stopped = True
                return 1
            # =====================================================
            case 0xF3:  # di
                self.di_armed = True
                return 1
            case 0xFB:  # ei
                self.ei_armed = True
                return 1
            # =====================================================
            case 0x07:  # rlca
                self.f = 0

                rotation = self._rotate_left_8(self.a)

                if rotation[0] == 0:
                    self.f |= CPUFlags.Z

                self.f |= CPUFlags.C & (rotation[1] << 4)
                self.a = rotation[0]

                return 1
            case 0x17:  # rla
                self.f = 0

                rotation = self._rotate_left_9(self._get_carry_and_n_as_9bit(self.a))

                self.a = rotation[0] & 0xFF
                self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                return 1
            case 0x0F:  # rrca
                self.f = 0

                rotation = self._rotate_right_8(self.a)

                if rotation[0] == 0:
                    self.f |= CPUFlags.Z

                self.f |= CPUFlags.C & (rotation[1] << 4)
                self.a = rotation[0]

                return 1
            case 0x1F:  # rra
                self.f = 0

                rotation = self._rotate_right_9(self._get_n_and_carry_as_9bit(self.a))

                self.a = rotation[0] & 0xFF
                self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                return 1

            # Some opcodes are prefixed with 0xCB
            case 0xCB:
                opcode2 = addrbus.read(self._advance_pc())
                match opcode2:
                    case 0x37:  # swap a
                        self.f = 0

                        lower_nibble = self.a & 0xF
                        upper_nibble = (self.a & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.a = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x30:  # swap b
                        self.f = 0

                        lower_nibble = self.b & 0xF
                        upper_nibble = (self.b & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.b = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x31:  # swap c
                        self.f = 0

                        lower_nibble = self.c & 0xF
                        upper_nibble = (self.c & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.c = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x32:  # swap d
                        self.f = 0

                        lower_nibble = self.d & 0xF
                        upper_nibble = (self.d & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.d = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x33:  # swap e
                        self.f = 0

                        lower_nibble = self.e & 0xF
                        upper_nibble = (self.e & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.e = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x34:  # swap h
                        self.f = 0

                        lower_nibble = self.h & 0xF
                        upper_nibble = (self.h & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.h = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x35:  # swap l
                        self.f = 0

                        lower_nibble = self.l & 0xF
                        upper_nibble = (self.l & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        self.l = (lower_nibble << 4) | upper_nibble
                        return 2
                    case 0x36:  # swap [hl]
                        value = addrbus.read(self.hl)

                        self.f = 0

                        lower_nibble = value & 0xF
                        upper_nibble = (value & 0xF0) >> 4

                        if ((lower_nibble << 4) | upper_nibble) == 0:
                            self.f |= CPUFlags.Z

                        value = (lower_nibble << 4) | upper_nibble
                        addrbus.write(self.hl, value)
                        return 4
                    # =====================================================
                    case 0x07:  # rlc a
                        self.f = 0

                        rotation = self._rotate_left_8(self.a)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.a = rotation[0]

                        return 2
                    case 0x00:  # rlc b
                        self.f = 0

                        rotation = self._rotate_left_8(self.b)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.b = rotation[0]

                        return 2
                    case 0x01:  # rlc c
                        self.f = 0

                        rotation = self._rotate_left_8(self.c)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.c = rotation[0]

                        return 2
                    case 0x02:  # rlc d
                        self.f = 0

                        rotation = self._rotate_left_8(self.d)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.d = rotation[0]

                        return 2
                    case 0x03:  # rlc e
                        self.f = 0

                        rotation = self._rotate_left_8(self.e)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.e = rotation[0]

                        return 2
                    case 0x04:  # rlc h
                        self.f = 0

                        rotation = self._rotate_left_8(self.h)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.h = rotation[0]

                        return 2
                    case 0x05:  # rlc l
                        self.f = 0

                        rotation = self._rotate_left_8(self.l)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.l = rotation[0]

                        return 2
                    case 0x06:  # rlc [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)

                        rotation = self._rotate_left_8(value)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        addrbus.write(self.hl, rotation[0])

                        return 4
                    # =====================================================
                    case 0x17:  # rl a
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.a)
                        )

                        self.a = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x10:  # rl b
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.b)
                        )

                        self.b = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x11:  # rl c
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.c)
                        )

                        self.c = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x12:  # rl d
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.d)
                        )

                        self.d = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x13:  # rl e
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.e)
                        )

                        self.e = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x14:  # rl h
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.h)
                        )

                        self.h = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x15:  # rl l
                        self.f = 0

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(self.l)
                        )

                        self.l = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        return 2
                    case 0x16:  # rl [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)

                        rotation = self._rotate_left_9(
                            self._get_carry_and_n_as_9bit(value)
                        )

                        value = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x100) >> 4)

                        addrbus.write(self.hl, value)
                        return 4
                    # =====================================================
                    case 0x0F:  # rrc a
                        self.f = 0

                        rotation = self._rotate_right_8(self.a)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.a = rotation[0]

                        return 2
                    case 0x08:  # rrc b
                        self.f = 0

                        rotation = self._rotate_right_8(self.b)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.b = rotation[0]

                        return 2
                    case 0x09:  # rrc c
                        self.f = 0

                        rotation = self._rotate_right_8(self.c)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.c = rotation[0]

                        return 2
                    case 0x0A:  # rrc d
                        self.f = 0

                        rotation = self._rotate_right_8(self.d)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.d = rotation[0]

                        return 2
                    case 0x0B:  # rrc e
                        self.f = 0

                        rotation = self._rotate_right_8(self.e)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.e = rotation[0]

                        return 2
                    case 0x0C:  # rrc h
                        self.f = 0

                        rotation = self._rotate_right_8(self.h)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.h = rotation[0]

                        return 2
                    case 0x0D:  # rrc l
                        self.f = 0

                        rotation = self._rotate_right_8(self.l)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        self.l = rotation[0]

                        return 2
                    case 0x0E:  # rrc [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)

                        rotation = self._rotate_right_8(value)

                        if rotation[0] == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (rotation[1] << 4)
                        value = rotation[0]

                        addrbus.write(self.hl, value)
                        return 4
                    # =====================================================
                    case 0x1F:  # rr a
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.a)
                        )

                        self.a = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x18:  # rr b
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.b)
                        )

                        self.b = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x19:  # rr c
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.c)
                        )

                        self.c = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x1A:  # rr d
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.d)
                        )

                        self.d = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x1B:  # rr e
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.e)
                        )

                        self.e = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x1C:  # rr h
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.h)
                        )

                        self.h = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x1D:  # rr l
                        self.f = 0

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(self.l)
                        )

                        self.l = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        return 2
                    case 0x1E:  # rr [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)

                        rotation = self._rotate_right_9(
                            self._get_n_and_carry_as_9bit(value)
                        )

                        value = rotation[0] & 0xFF
                        self.f |= CPUFlags.C & ((rotation[0] & 0x1) << 4)

                        addrbus.write(self.hl, value)
                        return 4
                    # =====================================================
                    case 0x27:  # sla a
                        self.f = 0

                        shifted = (self.a << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.a << 1) & 0x100) >> 4)
                        self.a = shifted
                        return 2
                    case 0x20:  # sla b
                        self.f = 0

                        shifted = (self.b << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.b << 1) & 0x100) >> 4)
                        self.b = shifted
                        return 2
                    case 0x21:  # sla c
                        self.f = 0

                        shifted = (self.c << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.c << 1) & 0x100) >> 4)
                        self.c = shifted
                        return 2
                    case 0x22:  # sla d
                        self.f = 0

                        shifted = (self.d << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.d << 1) & 0x100) >> 4)
                        self.d = shifted
                        return 2
                    case 0x23:  # sla e
                        self.f = 0

                        shifted = (self.e << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.e << 1) & 0x100) >> 4)
                        self.e = shifted
                        return 2
                    case 0x24:  # sla h
                        self.f = 0

                        shifted = (self.h << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.h << 1) & 0x100) >> 4)
                        self.h = shifted
                        return 2
                    case 0x25:  # sla l
                        self.f = 0

                        shifted = (self.l << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((self.l << 1) & 0x100) >> 4)
                        self.l = shifted
                        return 2
                    case 0x26:  # sla [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)
                        shifted = (value << 1) & 0xFF

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & (((value << 1) & 0x100) >> 4)
                        value = shifted

                        addrbus.write(self.hl, value)
                        return 4
                    # =====================================================
                    case 0x2F:  # sra a
                        self.f = 0

                        shifted = (self.a >> 1) | (self.a & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.a & 0x1) << 4)
                        self.a = shifted
                        return 2
                    case 0x28:  # sra b
                        self.f = 0

                        shifted = (self.b >> 1) | (self.b & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.b & 0x1) << 4)
                        self.b = shifted
                        return 2
                    case 0x29:  # sra c
                        self.f = 0

                        shifted = (self.c >> 1) | (self.c & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.c & 0x1) << 4)
                        self.c = shifted
                        return 2
                    case 0x2A:  # sra d
                        self.f = 0

                        shifted = (self.d >> 1) | (self.d & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.d & 0x1) << 4)
                        self.d = shifted
                        return 2
                    case 0x2B:  # sra e
                        self.f = 0

                        shifted = (self.e >> 1) | (self.e & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.e & 0x1) << 4)
                        self.e = shifted
                        return 2
                    case 0x2C:  # sra h
                        self.f = 0

                        shifted = (self.h >> 1) | (self.h & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.h & 0x1) << 4)
                        self.h = shifted
                        return 2
                    case 0x2D:  # sra l
                        self.f = 0

                        shifted = (self.l >> 1) | (self.l & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.l & 0x1) << 4)
                        self.l = shifted
                        return 2
                    case 0x2E:  # sra [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)

                        shifted = (value >> 1) | (value & 0x80)

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((value & 0x1) << 4)
                        value = shifted

                        addrbus.write(self.hl, value)
                        return 4
                    # =====================================================
                    case 0x3F:  # srl a
                        self.f = 0

                        shifted = self.a >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.a & 0x1) << 4)
                        self.a = shifted
                        return 2
                    case 0x38:  # srl b
                        self.f = 0

                        shifted = self.b >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.b & 0x1) << 4)
                        self.b = shifted
                        return 2
                    case 0x39:  # srl c
                        self.f = 0

                        shifted = self.c >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.c & 0x1) << 4)
                        self.c = shifted
                        return 2
                    case 0x3A:  # srl d
                        self.f = 0

                        shifted = self.d >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.d & 0x1) << 4)
                        self.d = shifted
                        return 2
                    case 0x3B:  # srl e
                        self.f = 0

                        shifted = self.e >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.e & 0x1) << 4)
                        self.e = shifted
                        return 2
                    case 0x3C:  # srl h
                        self.f = 0

                        shifted = self.h >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.h & 0x1) << 4)
                        self.h = shifted
                        return 2
                    case 0x3D:  # srl l
                        self.f = 0

                        shifted = self.l >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((self.l & 0x1) << 4)
                        self.l = shifted
                        return 2
                    case 0x3E:  # srl [hl]
                        self.f = 0

                        value = addrbus.read(self.hl)

                        shifted = value >> 1

                        if shifted == 0:
                            self.f |= CPUFlags.Z

                        self.f |= CPUFlags.C & ((value & 0x1) << 4)
                        value = shifted

                        addrbus.write(self.hl, value)
                        return 4

                raise IllegalInstruction(
                    f"Unknown opcode {hex(opcode)} {hex(opcode2)} at {hex(self.pc)}"
                )

        raise IllegalInstruction(f"Unknown opcode {hex(opcode)} at {hex(self.pc)}")
