# Scene3 — Stage 3: Unity Runtime Scene Reconstruction (`App/Unity`)

**Last Updated:** November 24, 2026  
**Scope:** Stage 3 Deliverable — Converting Stage 2 (`3DETR`) 3D object detections into live, interactive Unity scenes at **game time (runtime)**.

## 1. Overview & Goal
Stage 3 takes a 2D indoor image, passes it through our Python ML backend (Stage 1 Depth Estimation + Stage 2 `3DETR` Object Detection), and dynamically reconstructs the 3D environment inside Unity **while the game is running (Play Mode / Compiled Build)** so users can watch the scene assemble in real time.

Both upload workflows feed into the **exact same core C# reconstruction pipeline** 
Ex: (`RuntimeSceneReconstructor`).

## 2. Two Image Upload Workflows (Both Execute in Game Time)

The Unity app provides two entry points that trigger reconstruction during runtime:

### Workflow A: Developer Tool / Custom Editor Window (Play Mode)
* **How it works:** A custom Unity `EditorWindow` (`Scene3DevWindow`) docked in the Unity Editor provides a **drag-and-drop image box** (`EditorGUILayout.ObjectField` / `DragAndDrop` zone).
* **Game-Time Execution:** When a developer drops an image (or test JSON) into the tool and clicks **Reconstruct**, the script automatically enters/uses **Play Mode** (`EditorApplication.isPlaying = true`), sends the image to the backend, and runs the runtime C# builder so you watch the 3D scene generate live in the Game view.
* **Offline JSON Override:** Developers can also drop a mock `.json` file directly into this window to test scene reconstruction without running the Python GPU server.

### Workflow B: In-Game Player UI (Runtime Gameplay)
* Unity does **not** natively support dragging files from your desktop directly onto a game window.
* **Recommended Approach:** Provide a clean in-game **Upload Image** button (Canvas UI) that opens a **native OS file picker dialog** (via a lightweight cross-platform wrapper such as `UnityStandaloneFileBrowser` or a custom in-game folder browser).
* **Game-Time Execution:** Once the player selects an image file (`.jpg` / `.png`), Unity loads it into a `Texture2D`, sends it to the Python backend, receives the JSON detections, and invokes the exact same `RuntimeSceneReconstructor` script to spawn the room live in front of the player.

---

## 3. End-to-End Architecture & Tech Stack

```text
[User Image (.jpg/.png)]
   ├── Workflow A: Custom Editor Drag-and-Drop Window (enters Play Mode)
   └── Workflow B: In-Game UI Button -> Native File Dialog
          │
          ▼  (HTTP POST via UnityWebRequest)
[Python Backend: Stage 1 (Depth Anything) -> Stage 2 (3DETR)]
          │
          ▼  (Returns JSON Detection List)
[Core C# Runtime Pipeline: RuntimeSceneReconstructor.