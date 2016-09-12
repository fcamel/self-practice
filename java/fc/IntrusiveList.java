//------------------------------------------------------------------------------
// Just demostrate the concept. No strict test and protection for incorrect usages.
//------------------------------------------------------------------------------

package fc;

public class IntrusiveList<T>
{
    private Node<T> head;
    private Node<T> tail;
    private int identifier;

    public IntrusiveList(int identifier) {
        this.identifier = identifier;
    }

    public Node<T> Head() {
        return head;
    }

    public Node<T> Tail() {
        return tail;
    }

    public void Append(NodeValue<T> value) {
        Node<T> node = value.GetNode(identifier);
        if (tail == null) {
            head = tail = node;
            return;
        }
        tail.InsertAfter(node);
        tail = node;
    }

    public void InsertBefore(NodeValue<T> base, NodeValue<T> newValue) {
        Node<T> newNode = newValue.GetNode(identifier);
        Node<T> baseNode = base.GetNode(identifier);

        newNode.Delete();
        baseNode.InsertBefore(newNode);
        if (baseNode == head)
            head = newNode;
    }

    public void InsertAfter(NodeValue<T> base, NodeValue<T> newValue) {
        Node<T> newNode = newValue.GetNode(identifier);
        Node<T> baseNode = base.GetNode(identifier);

        newNode.Delete();
        baseNode.InsertAfter(newNode);
        if (baseNode == tail)
            tail = newNode;
    }

    public void Delete(NodeValue<T> value) {
        Node<T> node = value.GetNode(identifier);
        Node<T> next = node.GetNext();
        Node<T> prev = node.GetPrev();

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
