//------------------------------------------------------------------------------
// Intrusive List
//
// Just demostrate the concept. No strict test and protection for incorrect usages.
//------------------------------------------------------------------------------

// T is the target class which manages by List.
interface NodeValue<T>
{
    // If you want to be stored in multiple lists,
    // use identifier to distinguish the lists.
    Node<T> GetNode(String identifier);
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
    private Node<T> head;
    private Node<T> tail;
    String identifier;

    List(String identifier) {
        this.identifier = identifier;
    }

    Node<T> Head() {
        return head;
    }

    Node<T> Tail() {
        return tail;
    }

    void Append(NodeValue<T> value) {
        Node<T> node = value.GetNode(identifier);
        if (tail == null) {
            head = tail = node;
            return;
        }
        tail.InsertAfter(node);
        tail = node;
    }

    void InsertBefore(NodeValue<T> base, NodeValue<T> newValue) {
        Node<T> newNode = newValue.GetNode(identifier);
        Node<T> baseNode = base.GetNode(identifier);

        newNode.Delete();
        baseNode.InsertBefore(newNode);
        if (baseNode == head)
            head = newNode;
    }

    void InsertAfter(NodeValue<T> base, NodeValue<T> newValue) {
        Node<T> newNode = newValue.GetNode(identifier);
        Node<T> baseNode = base.GetNode(identifier);

        newNode.Delete();
        baseNode.InsertAfter(newNode);
        if (baseNode == tail)
            tail = newNode;
    }

    void Delete(NodeValue<T> value) {
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

    boolean Empty() {
        return head == null;
    }
}

//------------------------------------------------------------------------------
// End of IntrusiveList
//------------------------------------------------------------------------------

class Item implements NodeValue<Item>
{
    private Node<Item> node1;
    private Node<Item> node2;
    private String value;

    Item(String value)
    {
        this.value = value;
        node1 = new Node<Item>(this);
        node2 = new Node<Item>(this);
    }

    String GetValue()
    {
        return value;
    }

    @Override
    public Node<Item> GetNode(String identifier)
    {
        // NOTE: Just demonstrate that it can be put in more than one list.
        // If you'd like to support many lists, use a Map to store Node<Item>.
        if (identifier == "another")
            return node1;
        else
            return node2;
    }
}


public class TestIntrusiveList
{
    static void OutputList(List<Item> list) {
        Node<Item> current = list.Head();
        boolean first = true;
        while (current != null) {
            if (!first) {
                System.out.print(", ");
            }
            System.out.print(current.GetValue().GetValue());
            first = false;
            current = current.GetNext();
        }
        System.out.println();
    }

    public static void main(String[] args) {
        // The identifier "default" and "another" below are defined in Item.
        // We need to expose the info to access the corresponding Node<Item> inside Item.
        List<Item> list = new List<Item>("default");
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

        c.GetNode("default").Delete();
        d.GetNode("default").Delete();
        System.out.println("Delete c and d");
        OutputList(list);

        System.out.println("Expect d, a, c, b, e");
        list.InsertAfter(a, c);
        list.InsertBefore(a, d);
        OutputList(list);

        System.out.println("Expect d, c, b, e, a");
        list.InsertAfter(e, a);
        OutputList(list);

        System.out.println("Create another list with \"c d e\"");
        List<Item> list2 = new List<Item>("another");
        list2.Append(c);
        list2.Append(d);
        list2.Append(e);
        OutputList(list2);

        System.out.println("Expect <d, c, b, e, a> and <c, b, d, e>");
        list2.InsertAfter(c, b);
        OutputList(list);
        System.out.println("---");
        OutputList(list2);
    }
}
