using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerController : MonoBehaviour
{
    public float speed = 5.0f;
    public float turnSpeed = 100.0f;
    public InputAction moveAction;
    public Vector2 moveInput;

    void Start()
    {
        moveAction.Enable();
    }

    void Update()
    {
        moveInput = moveAction.ReadValue<Vector2>();

        // Moves forward/backward relative to where the Player is currently facing (Space.Self)
        transform.Translate(Vector3.forward * speed * Time.deltaTime * moveInput.y);

        // Rotates left/right around the vertical Y axis
        transform.Rotate(Vector3.up * turnSpeed * Time.deltaTime * moveInput.x);
    }
}