# Scene3 — Unity Scene Builder (`App/Unity`)

**Last Updated:** November 28, 2026

## 1. How It Works (Architecture)

Everything happens **in game time (Play Mode)** so you can see the room get built live in front of you. There are two ways to upload an image, and both use the exact same C# builder script:

```text
[2D Image (.jpg / .png)]
   ├── Way 1 (For Devs): Unity Editor DropBox Window
   └── Way 2 (For Players): In-Game "Upload Image" Button (Coming Soon)
          │
          ▼
[Stage 2 Backend] -> Finds objects in the image & sends back a JSON list
          │
          ▼
[SandboxSceneManager.cs] -> Reads the JSON & spawns matching 3D prefabs in-game
```

### How the Editor Tool Talks to the Game
* **`Scene3DropBoxWindow.cs`** (inside `Assets/Editor/`): This is a custom window inside the Unity Editor. When you drop an image into it and click **Reconstruct in Game Time**, it saves the image's file path and automatically hits **Play** in Unity.
* **`SandboxSceneManager.cs`** (attached to the `SceneManager` object in the scene): As soon as the game starts, this script grabs that saved image path, loads the image, and runs the scene-building logic.

---

## 2. How to Use the Editor DropBox Tool

Follow these steps to test uploading an image in the Unity Editor:

1. **Open the DropBox Window:**
   * Look at the very top menu bar in Unity (next to *File*, *Edit*, *Assets*).
   * Click **`Scene3`** -> **`DropBox Window`**.
   * *(Tip: Drag the **Scene3 DropBox** tab next to your **Inspector** tab on the right so it stays docked and easy to reach).*
2. **Add an Image:**
   * Drag any `.png` or `.jpg` image from your computer's folder directly into the **`Drag & Drop Image Here`** box, **or**
   * Click the small circle icon next to **`Project Image`** to pick an image already inside your Unity `Assets` folder.
   * You will see a small preview of your image appear below the box.
3. **Build in Game Time:**
   * Click the **`Reconstruct in Game Time`** button.
   * Unity will automatically enter **Play Mode** and spawn the reconstructed objects on the floor in front of your player. *(Currently spawns a test cube until we hook up the real Stage 2 JSON list).*

---

## 3. How to Play the Sandbox (Controls)

Once you are in Play Mode, you can walk around the flat floor to look at the spawned objects from different angles:

| Key | What It Does |
| :--- | :--- |
| **`W` or `Up Arrow`** | Walk forward (in the direction your character is facing) |
| **`S` or `Down Arrow`** | Walk backward |
| **`A` or `Left Arrow`** | Turn left |
| **`D` or `Right Arrow`** | Turn right |

---

## 4. Project Files & Where Things Are

* **`Assets/Editor/Scene3DropBoxWindow.cs`**: Creates the `Scene3 -> DropBox Window` menu tool. *(Note: Do not attach this to any object in the scene—Unity loads it automatically).*
* **`Assets/Scripts/SandboxSceneManager.cs`**: Attached to the **`SceneManager`** object in the Hierarchy. Handles receiving the image and spawning 3D objects during Play Mode.
* **`Assets/Scripts/PlayerController.cs`**: Attached to the parent **`Player`** object (which holds both the character model and the camera). Controls walking and turning.

---

## 5. What We Are Building Next

1. **Real Prefab Spawning:** Replace the placeholder cube in `SandboxSceneManager.cs` with code that reads Stage 2's JSON list and spawns real 3D furniture prefabs at the right positions, rotations, and sizes (`1 Unity unit = 1 meter`).
2. **Fallback Box:** If Stage 2 detects an object it doesn't recognize, spawn a basic box matching that object's size so nothing is missing.
3. **In-Game Upload Button:** Connect the **`Upload Image`** button on the game screen (HUD) so players can pick an image during gameplay without needing the Unity Editor.