// Relay-kit — Dear ImGui theme (generated). C++11.
// Call ApplyRelayKitTheme() once after ImGui::CreateContext().
// Load fonts (optional) for full fidelity:
//   io.Fonts->AddFontFromFileTTF("fonts/Inter.ttf", 16.0f);
//   io.Fonts->AddFontFromFileTTF("fonts/JetBrainsMono.ttf", 15.0f);
#pragma once
#include "imgui.h"

inline void ApplyRelayKitTheme() {
    ImGuiStyle& s = ImGui::GetStyle();
    s.WindowRounding    = 12.0f;
    s.ChildRounding     = 8.0f;
    s.FrameRounding     = 8.0f;
    s.PopupRounding     = 8.0f;
    s.GrabRounding      = 8.0f;
    s.TabRounding       = 8.0f;
    s.WindowPadding     = ImVec2(16, 16);
    s.FramePadding      = ImVec2(12, 8);
    s.ItemSpacing       = ImVec2(12, 8);
    s.ScrollbarSize     = 12.0f;
    s.WindowBorderSize  = 1.0f;
    s.FrameBorderSize   = 1.0f;

    ImVec4* col = s.Colors;
    col[ImGuiCol_WindowBg]        = ImVec4(0.082f, 0.078f, 0.059f, 1.00f);
    col[ImGuiCol_ChildBg]         = ImVec4(0.125f, 0.118f, 0.090f, 1.00f);
    col[ImGuiCol_PopupBg]         = ImVec4(0.149f, 0.137f, 0.106f, 1.00f);
    col[ImGuiCol_Border]          = ImVec4(0.200f, 0.173f, 0.133f, 1.00f);
    col[ImGuiCol_Text]            = ImVec4(0.949f, 0.922f, 0.867f, 1.00f);
    col[ImGuiCol_TextDisabled]    = ImVec4(0.612f, 0.573f, 0.518f, 1.00f);
    col[ImGuiCol_FrameBg]         = ImVec4(0.149f, 0.137f, 0.106f, 1.00f);
    col[ImGuiCol_FrameBgHovered]  = ImVec4(0.200f, 0.173f, 0.133f, 1.00f);
    col[ImGuiCol_FrameBgActive]   = ImVec4(0.055f, 0.141f, 0.110f, 1.00f);
    col[ImGuiCol_TitleBg]         = ImVec4(0.149f, 0.137f, 0.106f, 1.00f);
    col[ImGuiCol_TitleBgActive]   = ImVec4(0.149f, 0.137f, 0.106f, 1.00f);
    col[ImGuiCol_Button]          = ImVec4(0.204f, 0.827f, 0.600f, 0.14f);
    col[ImGuiCol_ButtonHovered]   = ImVec4(0.204f, 0.827f, 0.600f, 0.30f);
    col[ImGuiCol_ButtonActive]    = ImVec4(0.204f, 0.827f, 0.600f, 1.00f);
    col[ImGuiCol_Header]          = ImVec4(0.204f, 0.827f, 0.600f, 0.18f);
    col[ImGuiCol_HeaderHovered]   = ImVec4(0.204f, 0.827f, 0.600f, 0.32f);
    col[ImGuiCol_HeaderActive]    = ImVec4(0.204f, 0.827f, 0.600f, 1.00f);
    col[ImGuiCol_CheckMark]       = ImVec4(0.204f, 0.827f, 0.600f, 1.00f);
    col[ImGuiCol_SliderGrab]      = ImVec4(0.204f, 0.827f, 0.600f, 1.00f);
    col[ImGuiCol_SliderGrabActive]= ImVec4(0.431f, 0.906f, 0.718f, 1.00f);
    col[ImGuiCol_Tab]             = ImVec4(0.149f, 0.137f, 0.106f, 1.00f);
    col[ImGuiCol_TabActive]       = ImVec4(0.204f, 0.827f, 0.600f, 0.28f);
    col[ImGuiCol_TabHovered]      = ImVec4(0.204f, 0.827f, 0.600f, 0.20f);
    col[ImGuiCol_PlotLines]       = ImVec4(0.204f, 0.827f, 0.600f, 1.00f);
    col[ImGuiCol_PlotHistogram]   = ImVec4(0.204f, 0.827f, 0.600f, 1.00f);
    col[ImGuiCol_Separator]       = ImVec4(0.200f, 0.173f, 0.133f, 1.00f);
    col[ImGuiCol_ScrollbarBg]     = ImVec4(0.082f, 0.078f, 0.059f, 1.00f);
    col[ImGuiCol_ScrollbarGrab]   = ImVec4(0.200f, 0.173f, 0.133f, 1.00f);
}
