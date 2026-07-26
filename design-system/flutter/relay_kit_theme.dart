// Relay-kit — Flutter theme (generated). Requires google_fonts (or bundle fonts).
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class RelayKit {
  static const ColorScheme light = ColorScheme(
    brightness: Brightness.light,
    surface: Color(0xFFFAF6EF), onSurface: Color(0xFF22201C),
    primary: Color(0xFF059669), onPrimary: Color(0xFFFFFFFF),
    secondary: Color(0xFF047857), onSecondary: Color(0xFFFFFFFF),
    error: Color(0xFFC0392B), onError: Color(0xFFFFFFFF),
    outline: Color(0xFFE8DFCF),
  );
  static const ColorScheme dark = ColorScheme(
    brightness: Brightness.dark,
    surface: Color(0xFF15140F), onSurface: Color(0xFFF2EBDD),
    primary: Color(0xFF34D399), onPrimary: Color(0xFF08130D),
    secondary: Color(0xFF6EE7B7), onSecondary: Color(0xFF08130D),
    error: Color(0xFFE1685A), onError: Color(0xFFFFFFFF),
    outline: Color(0xFF332C22),
  );

  static ThemeData theme({bool dark = false}) {
    final cs = dark ? RelayKit.dark : RelayKit.light;
    final base = ThemeData(useMaterial3: true, colorScheme: cs, scaffoldBackgroundColor: cs.surface);
    return base.copyWith(
      textTheme: GoogleFonts.interTextTheme(base.textTheme).copyWith(
        displaySmall: GoogleFonts.fraunces(fontSize: 40, fontWeight: FontWeight.w500, color: cs.onSurface),
        headlineSmall: GoogleFonts.fraunces(fontSize: 24, fontWeight: FontWeight.w500, color: cs.onSurface),
      ),
      cardTheme: CardTheme(color: Color(0xFFFFFFFF), elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: cs.outline))),
      filledButtonTheme: FilledButtonThemeData(style: FilledButton.styleFrom(
        backgroundColor: cs.primary, foregroundColor: cs.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)))),
    );
  }
}
