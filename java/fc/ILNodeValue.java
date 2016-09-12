package fc;

// T is the target class which manages by IntrusiveList.
public interface ILNodeValue<T>
{
    // If you want to be stored in multiple lists,
    // use identifier to distinguish the lists.
    ILNode<T> GetNode(int identifier);
}
