package fc;

public class Node<T>
{
    private T value;
    private Node<T> next;
    private Node<T> prev;

    public Node(T value)
    {
        this.value = value;
    }

    public T GetValue()
    {
        return value;
    }

    public Node<T> GetNext()
    {
        return next;
    }

    public Node<T> GetPrev()
    {
        return prev;
    }

    public void Delete()
    {
        if (prev != null)
            prev.next = next;
        if (next != null)
            next.prev = prev;
    }

    //-----------------------------------------------------
    // Internal API
    //-----------------------------------------------------

    // Hide this from the users to keep the states in IntrusiveList correct.
    void InsertBefore(Node<T> node)
    {
        if (node == null) {
            return;
        }
        if (prev != null)
            prev.next = node;
        node.prev = prev;
        node.next = this;
        prev = node;
    }

    // Hide this from the users to keep the states in IntrusiveList correct.
    void InsertAfter(Node<T> node)
    {
        if (node == null) {
            return;
        }
        node.next = next;
        if (next != null)
            next.prev = node;
        next = node;
        node.prev = this;
    }
}
