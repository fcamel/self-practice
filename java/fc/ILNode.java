package fc;

public class ILNode<T>
{
    private T value;
    private ILNode<T> next;
    private ILNode<T> prev;

    public ILNode(T value)
    {
        this.value = value;
    }

    public T GetValue()
    {
        return value;
    }

    public ILNode<T> GetNext()
    {
        return next;
    }

    public ILNode<T> GetPrev()
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
    void InsertBefore(ILNode<T> node)
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
    void InsertAfter(ILNode<T> node)
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
