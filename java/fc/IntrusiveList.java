//------------------------------------------------------------------------------
// Just demostrate the concept. No strict test and protection for incorrect usages.
//------------------------------------------------------------------------------

package fc;

public class IntrusiveList<T>
{
    private ILNode<T> head;
    private ILNode<T> tail;
    private int identifier;

    public IntrusiveList(int identifier) {
        this.identifier = identifier;
    }

    public ILNode<T> Head() {
        return head;
    }

    public ILNode<T> Tail() {
        return tail;
    }

    public void Append(ILNodeValue<T> value) {
        ILNode<T> node = value.GetNode(identifier);
        if (tail == null) {
            head = tail = node;
            return;
        }
        tail.InsertAfter(node);
        tail = node;
    }

    public void InsertBefore(ILNodeValue<T> base, ILNodeValue<T> newValue) {
        ILNode<T> newNode = newValue.GetNode(identifier);
        ILNode<T> baseNode = base.GetNode(identifier);

        newNode.Delete();
        baseNode.InsertBefore(newNode);
        if (baseNode == head)
            head = newNode;
    }

    public void InsertAfter(ILNodeValue<T> base, ILNodeValue<T> newValue) {
        ILNode<T> newNode = newValue.GetNode(identifier);
        ILNode<T> baseNode = base.GetNode(identifier);

        newNode.Delete();
        baseNode.InsertAfter(newNode);
        if (baseNode == tail)
            tail = newNode;
    }

    public void Delete(ILNodeValue<T> value) {
        ILNode<T> node = value.GetNode(identifier);
        ILNode<T> next = node.GetNext();
        ILNode<T> prev = node.GetPrev();

        node.Delete();

        if (node == head) {
            head = next;
        }
        if (node == tail) {
            tail = prev;
        }
    }

    public boolean Empty() {
        return head == null;
    }
}
