//------------------------------------------------------------------------------
// Intrusive List
//------------------------------------------------------------------------------

// T is the target class which manages by List.
interface NodeValue<T>
{
    Node<T> GetNode();
}

// The inernal implementation for List.
class Node<T>
{
    private T value;
    private Node<T> next;
    private Node<T> prev;

    Node(T value)
    {
        this.value = value;
    }

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

    void Delete()
    {
        if (prev != null)
            prev.next = next;
        if (next != null)
            next.prev = prev;
    }

    Node<T> GetNext()
    {
        return next;
    }

    Node<T> GetPrev()
    {
        return prev;
    }

    T GetValue()
    {
        return value;
    }
}

// IntrusiveList.
class List<T>
{
    Node<T> Head()
    {
        return head;
    }

    Node<T> Tail()
    {
        return tail;
    }

    void Append(NodeValue<T> value) {
        Node<T> node = value.GetNode();
        if (tail == null) {
            head = tail = node;
            return;
        }
        tail.InsertAfter(node);
        tail = node;
    }

    void InsertBefore(NodeValue<T> base, NodeValue<T> newValue) {
        Node<T> newNode = newValue.GetNode();
        Node<T> baseNode = base.GetNode();

        newNode.Delete();
        baseNode.InsertBefore(newNode);
        if (baseNode == head)
            head = newNode;
    }

    void InsertAfter(NodeValue<T> base, NodeValue<T> newValue) {
        Node<T> newNode = newValue.GetNode();
        Node<T> baseNode = base.GetNode();

        newNode.Delete();
        baseNode.InsertAfter(newNode);
        if (baseNode == tail)
            tail = newNode;
    }

    void Delete(NodeValue<T> value) {
        Node<T> node = value.GetNode();
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

    boolean Empty() {
        return head == null;
    }

    Node<T> head;
    Node<T> tail;
}

//------------------------------------------------------------------------------
// End of IntrusiveList
//------------------------------------------------------------------------------

class Item implements NodeValue<Item>
{
    private Node<Item> node;
    private String value;

    Item(String value)
    {
        this.value = value;
        node = new Node<Item>(this);
    }

    String GetValue()
    {
        return value;
    }

    public Node<Item> GetNode()
    {
        return node;
    }
}


public class TestIntrusiveList
{
    static void OutputList(List<Item> list) {
        Node<Item> current = list.Head();
        while (current != null) {
            System.out.println(current.GetValue().GetValue());
            current = current.GetNext();
        }
    }

    public static void main(String[] args) {
        List<Item> list = new List<Item>();
        Item a = new Item("a");
        Item b = new Item("b");
        Item c = new Item("c");
        Item d = new Item("d");
        Item e = new Item("e");
        list.Append(a);
        list.Append(b);
        list.Append(c);
        list.Append(d);
        list.Append(e);

        System.out.println("Init");
        OutputList(list);

        c.GetNode().Delete();
        d.GetNode().Delete();
        System.out.println("Delete c and d");
        OutputList(list);

        System.out.println("Expect d, a, c, b, e");
        list.InsertAfter(a, c);
        list.InsertBefore(a, d);
        OutputList(list);

        System.out.println("Expect d, c, b, e, a");
        list.InsertAfter(e, a);
        OutputList(list);
    }
}
