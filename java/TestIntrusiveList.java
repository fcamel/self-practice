import fc.ILNode;
import fc.ILNodeValue;
import fc.IntrusiveList;

class Node extends ILNode<Item>
{
    Node(Item value)
    {
        super(value);
    }
}

class Item implements ILNodeValue<Item>
{
    // Indicate which list the item is stored.
    // With two identifiers, the item can be stored at most two lists.
    static int LIST_ID_DEFAULT = 0;
    static int LIST_ID_ANOTHER = 1;

    // Instead of using ArrayList, using array to reduce the access overhread.
    // However, Java doesn't support arrays of generic classes.
    // We need to create a subclass to workaround this.
    // See http://stackoverflow.com/a/7131673/278456
    private final Node[] nodes;
    private String value;

    Item(String value)
    {
        this.value = value;
        nodes = new Node[2];
        for (int i = 0; i < nodes.length; i++) {
            nodes[i] = new Node(this);
        }
    }

    String GetValue()
    {
        return value;
    }

    @Override
    public ILNode<Item> GetNode(int identifier)
    {
        return nodes[identifier];
    }
}


public class TestIntrusiveList
{
    static void OutputList(IntrusiveList<Item> list) {
        ILNode<Item> current = list.Head();
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
        IntrusiveList<Item> list = new IntrusiveList<Item>(Item.LIST_ID_DEFAULT);
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

        c.GetNode(Item.LIST_ID_DEFAULT).Delete();
        d.GetNode(Item.LIST_ID_DEFAULT).Delete();
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
        IntrusiveList<Item> list2 = new IntrusiveList<Item>(Item.LIST_ID_ANOTHER);
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
