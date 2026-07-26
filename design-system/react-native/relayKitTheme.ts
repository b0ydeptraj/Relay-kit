// Relay-kit — React Native theme (generated). Bundle fonts via expo-font / react-native.config.js.
export const relayKit = {
  color: { light: {"bg": "#FAF6EF", "surface": "#FFFFFF", "surface2": "#F3ECDF", "ink": "#22201C", "inkSoft": "#4A443B", "muted": "#6E665A", "line": "#E8DFCF", "lineSoft": "#F0E9DB", "primary": "#059669", "primaryDeep": "#047857", "primaryTint": "#DBF3EA", "onPrimary": "#FFFFFF", "success": "#059669", "warning": "#B7791F", "danger": "#C0392B", "info": "#2F6DB0", "band": "#14120D", "onBand": "#F3ECDD"}, dark: {"bg": "#15140F", "surface": "#201E17", "surface2": "#26231B", "ink": "#F2EBDD", "inkSoft": "#D6CDBB", "muted": "#9C9284", "line": "#332C22", "lineSoft": "#2A241B", "primary": "#34D399", "primaryDeep": "#6EE7B7", "primaryTint": "#0E241C", "onPrimary": "#08130D", "success": "#34D399", "warning": "#E0A94B", "danger": "#E1685A", "info": "#7FA8DA", "band": "#0E0C09", "onBand": "#F3ECDD"} },
  font: {
    display: 'Fraunces', sans: 'Inter', mono: 'JetBrains Mono',
    size: {"displayXl": 56, "display": 40, "h1": 32, "h2": 24, "h3": 19, "bodyLg": 18, "body": 16, "small": 14, "caption": 12.5}, weight: {"regular": 400, "medium": 500, "semibold": 600, "bold": 700},
  },
  space: {"0": 0, "1": 4, "2": 8, "3": 12, "4": 16, "5": 24, "6": 32, "7": 48, "8": 64, "9": 96},
  radius: {"sm": 8, "md": 12, "lg": 16, "xl": 24, "pill": 999},
} as const;

// Example:
// const c = relayKit.color[scheme];  // scheme = 'light' | 'dark'
// <View style={{ backgroundColor: c.surface, borderColor: c.line, borderRadius: relayKit.radius.md }} />
// <Text style={{ color: c.primary, fontFamily: relayKit.font.display }} />
