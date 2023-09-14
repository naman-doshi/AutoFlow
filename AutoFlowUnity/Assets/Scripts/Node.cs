using UnityEngine;

public class Node : MonoBehaviour
{
    [HideInInspector] public Segment segment;

    private int _id;

    public int Id
    {
        get => _id;
        set
        {
            _id = value;
            name = "Node" + _id;
        }
    }

    public void Reset()
    {
        tag = "Node";
    }
}
