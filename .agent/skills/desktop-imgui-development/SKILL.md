---
name: desktop-imgui-development
description: Use when building a desktop GUI with Dear ImGui (C++ or bindings): operator panels, real-time dashboards, debug overlays, game cheats UI, or tool UIs embedded in a render loop.
---

# Mission
Build functional, well-structured Dear ImGui interfaces with correct render loop integration and layout discipline.

## Mandatory scope
1. Declare backend: OpenGL3+GLFW, DirectX11/12, Vulkan, or SDL2 — each has a different backend setup.
2. Render loop structure: NewFrame -> layout logic -> Render -> present — no business logic inside render loop.
3. State separation: UI state lives in a dedicated struct, not scattered in render functions.
4. Font loading: custom fonts loaded in ImGui_ImplXxx_CreateFontsTexture, not per-frame.
5. DPI awareness: implement ImGui::GetIO().DisplayFramebufferScale or DPI scale factor.
6. For overlay injection (game cheats): document hook point (Present hook, manual map) and cleanup.

## Evidence contract
- backend declared
- render loop structure documented
- state struct defined
- compiles and renders correct layout
- DPI handling documented

## Role
- imgui-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- UI spec or wireframe
- backend (DirectX/OpenGL/Vulkan)
- C++ project context
- MMO operation live state (from mmo-cloud-operations, mmo-proxy-network-ops) for control panel data

## Outputs
- ImGui implementation
- render loop integration
- state management code

## Reference skills and rules
- Never put business logic inside the render loop — it runs every frame.
- UI state must be a separate struct, not global variables.
- Font atlas must be built once at init, not per-frame.
- For overlay injection, document cleanup on process exit or eject.
- Open `references/desktop-imgui-development-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/desktop-imgui-development-good-output.md` and `examples/desktop-imgui-development-bad-output.md` to calibrate output quality.
- Use `evals/desktop-imgui-development-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/desktop-imgui-development-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- cpp-systems-engineering
- windows-native-internals
- test-hub
- field-journal-evolution
