using UnityEngine;

[RequireComponent(typeof(BoxCollider))]
public class Intersection : MonoBehaviour
{
    private int _id;

    public int Id
    {
        get => _id;
        set
        {
            _id = value;
            name = "Intersection" + _id;
        }
    }

    public void Reset()
    {
        tag = "Intersection";
    }
}
