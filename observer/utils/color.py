from typing import List


class Colors():
    """ 색상 클래스. 인스턴스 생성 불가능.
    
        Static Attributes:
            red (dict),
            pink (dict),
            purple (dict),
            deep_purple (dict),
            indigo (dict),
            blue (dict),
            light_blue (dict),
            cyan (dict),
            teal (dict),
            green (dict),
            light_green (dict),
            lime (dict),
            yellow (dict),
            amber (dict),
            orange (dict),
            deep_orange (dict),
            brown (dict),
            grey (dict),
            blue_grey (dict),
            all_colors (List[dict])
            all_shades (List[int])

        Static Methods:
            def _convert(hex: int) -> List[int]:
            def to_rgb(hex: int) -> List[int]:
            def to_bgr(hex: int) -> List[int]:
    """

    red = {
        50: 0xFFFFEBEE,
        100: 0xFFFFCDD2,
        200: 0xFFEF9A9A,
        300: 0xFFE57373,
        400: 0xFFEF5350,
        500: 0xFFF44336,
        600: 0xFFE53935,
        700: 0xFFD32F2F,
        800: 0xFFC62828,
        900: 0xFFB71C1C,
    }
    pink = {
        50: 0xFFFCE4EC,
        100: 0xFFF8BBD0,
        200: 0xFFF48FB1,
        300: 0xFFF06292,
        400: 0xFFEC407A,
        500: 0xFFE91E63,
        600: 0xFFD81B60,
        700: 0xFFC2185B,
        800: 0xFFAD1457,
        900: 0xFF880E4F,
    }
    purple = {
        50: 0xFFF3E5F5,
        100: 0xFFE1BEE7,
        200: 0xFFCE93D8,
        300: 0xFFBA68C8,
        400: 0xFFAB47BC,
        500: 0xFF9C27B0,
        600: 0xFF8E24AA,
        700: 0xFF7B1FA2,
        800: 0xFF6A1B9A,
        900: 0xFF4A148C,
    }
    deep_purple = {
        50: 0xFFEDE7F6,
        100: 0xFFD1C4E9,
        200: 0xFFB39DDB,
        300: 0xFF9575CD,
        400: 0xFF7E57C2,
        500: 0xFF673AB7,
        600: 0xFF5E35B1,
        700: 0xFF512DA8,
        800: 0xFF4527A0,
        900: 0xFF311B92,
    }
    indigo = {
        50: 0xFFE8EAF6,
        100: 0xFFC5CAE9,
        200: 0xFF9FA8DA,
        300: 0xFF7986CB,
        400: 0xFF5C6BC0,
        500: 0xFF3F51B5,
        600: 0xFF3949AB,
        700: 0xFF303F9F,
        800: 0xFF283593,
        900: 0xFF1A237E,
    }
    blue = {
        50: 0xFFE3F2FD,
        100: 0xFFBBDEFB,
        200: 0xFF90CAF9,
        300: 0xFF64B5F6,
        400: 0xFF42A5F5,
        500: 0xFF2196F3,
        600: 0xFF1E88E5,
        700: 0xFF1976D2,
        800: 0xFF1565C0,
        900: 0xFF0D47A1,
    }
    light_blue = {
        50: 0xFFE1F5FE,
        100: 0xFFB3E5FC,
        200: 0xFF81D4FA,
        300: 0xFF4FC3F7,
        400: 0xFF29B6F6,
        500: 0xFF03A9F4,
        600: 0xFF039BE5,
        700: 0xFF0288D1,
        800: 0xFF0277BD,
        900: 0xFF01579B,
    }
    cyan = {
        50: 0xFFE0F7FA,
        100: 0xFFB2EBF2,
        200: 0xFF80DEEA,
        300: 0xFF4DD0E1,
        400: 0xFF26C6DA,
        500: 0xFF00BCD4,
        600: 0xFF00ACC1,
        700: 0xFF0097A7,
        800: 0xFF00838F,
        900: 0xFF006064,
    }
    teal = {
        50: 0xFFE0F2F1,
        100: 0xFFB2DFDB,
        200: 0xFF80CBC4,
        300: 0xFF4DB6AC,
        400: 0xFF26A69A,
        500: 0xFF009688,
        600: 0xFF00897B,
        700: 0xFF00796B,
        800: 0xFF00695C,
        900: 0xFF004D40,
    }
    green = {
        50: 0xFFE8F5E9,
        100: 0xFFC8E6C9,
        200: 0xFFA5D6A7,
        300: 0xFF81C784,
        400: 0xFF66BB6A,
        500: 0xFF4CAF50,
        600: 0xFF43A047,
        700: 0xFF388E3C,
        800: 0xFF2E7D32,
        900: 0xFF1B5E20,
    }
    light_green = {
        50: 0xFFF1F8E9,
        100: 0xFFDCEDC8,
        200: 0xFFC5E1A5,
        300: 0xFFAED581,
        400: 0xFF9CCC65,
        500: 0xFF8BC34A,
        600: 0xFF7CB342,
        700: 0xFF689F38,
        800: 0xFF558B2F,
        900: 0xFF33691E,
    }
    lime = {
        50: 0xFFF9FBE7,
        100: 0xFFF0F4C3,
        200: 0xFFE6EE9C,
        300: 0xFFDCE775,
        400: 0xFFD4E157,
        500: 0xFFCDDC39,
        600: 0xFFC0CA33,
        700: 0xFFAFB42B,
        800: 0xFF9E9D24,
        900: 0xFF827717,
    }
    yellow = {
        50: 0xFFFFFDE7,
        100: 0xFFFFF9C4,
        200: 0xFFFFF59D,
        300: 0xFFFFF176,
        400: 0xFFFFEE58,
        500: 0xFFFFEB3B,
        600: 0xFFFDD835,
        700: 0xFFFBC02D,
        800: 0xFFF9A825,
        900: 0xFFF57F17,
    }
    amber = {
        50: 0xFFFFF8E1,
        100: 0xFFFFECB3,
        200: 0xFFFFE082,
        300: 0xFFFFD54F,
        400: 0xFFFFCA28,
        500: 0xFFFFC107,
        600: 0xFFFFB300,
        700: 0xFFFFA000,
        800: 0xFFFF8F00,
        900: 0xFFFF6F00,
    }
    orange = {
        50: 0xFFFFF3E0,
        100: 0xFFFFE0B2,
        200: 0xFFFFCC80,
        300: 0xFFFFB74D,
        400: 0xFFFFA726,
        500: 0xFFFF9800,
        600: 0xFFFB8C00,
        700: 0xFFF57C00,
        800: 0xFFEF6C00,
        900: 0xFFE65100,
    }
    deep_orange = {
        50: 0xFFFBE9E7,
        100: 0xFFFFCCBC,
        200: 0xFFFFAB91,
        300: 0xFFFF8A65,
        400: 0xFFFF7043,
        500: 0xFFFF5722,
        600: 0xFFF4511E,
        700: 0xFFE64A19,
        800: 0xFFD84315,
        900: 0xFFBF360C,
    }
    brown = {
        50: 0xFFEFEBE9,
        100: 0xFFD7CCC8,
        200: 0xFFBCAAA4,
        300: 0xFFA1887F,
        400: 0xFF8D6E63,
        500: 0xFF795548,
        600: 0xFF6D4C41,
        700: 0xFF5D4037,
        800: 0xFF4E342E,
        900: 0xFF3E2723,
    }
    grey = {
        50: 0xFFFAFAFA,
        100: 0xFFF5F5F5,
        200: 0xFFEEEEEE,
        300: 0xFFE0E0E0,
        400: 0xFFBDBDBD,
        500: 0xFF9E9E9E,
        600: 0xFF757575,
        700: 0xFF616161,
        800: 0xFF424242,
        900: 0xFF212121,
    }
    blue_grey = {
        50: 0xFFECEFF1,
        100: 0xFFCFD8DC,
        200: 0xFFB0BEC5,
        300: 0xFF90A4AE,
        400: 0xFF78909C,
        500: 0xFF607D8B,
        600: 0xFF546E7A,
        700: 0xFF455A64,
        800: 0xFF37474F,
        900: 0xFF263238,
    }
    all_colors = [
        red,
        pink,
        purple,
        deep_purple,
        indigo,
        blue,
        light_blue,
        cyan,
        teal,
        green,
        light_green,
        lime,
        yellow,
        amber,
        orange,
        deep_orange,
        brown,
        grey,
        blue_grey,
    ]
    all_shades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]

    @staticmethod
    def _convert(hex: int) -> List[int]:
        r = (hex & 0xFF0000) >> 16
        g = (hex & 0x00FF00) >> 8
        b = (hex & 0x0000FF)
        return r, g, b

    @staticmethod
    def to_rgb(hex: int) -> List[int]:
        """ 16진수 색상을 8비트 RGB 색상(RGB888)으로 변환.

            Args:
                hex (int): 16진수 색상 코드.

            Returns:
                (List[int]): 8비트 RGB 색상 코드 [R,G,B].
        """
        return Colors._convert(hex)

    @staticmethod
    def to_bgr(hex: int) -> List[int]:
        """ 16진수 색상을 8비트 BGR 색상(BGR888)으로 변환.

            Args:
                hex (int): 16진수 색상 코드.

            Returns:
                (List[int]): 8비트 BGR 색상 코드 [B,G,R].
        """
        return Colors._convert(hex)[::-1]

    def __init__(self):
        # 인스턴스 생성 불가.
        raise RuntimeError('instance cannot be created.')
