#include <stdio.h>
#include <stdlib.h>

typedef struct node {
  struct node* next;
  int value;
} Node;

typedef struct list {
  Node* head;
} List;

Node* create_node(int value)
{
  Node* node = (Node*)malloc(sizeof(Node));
  node->next = NULL;
  node->value = value;
  return node;
}

void dump(List* list)
{
  if (!list || !list->head)
    return;

  printf("%d", list->head->value);
  Node* node =  list->head->next;
  while (node) {
    printf(", %d", node->value);
    node = node->next;
  }
  printf("\n");
}

// Refernece: https://www.ted.com/talks/linus_torvalds_the_mind_behind_linux
void remove_list_node_v1(List* list, Node* target)
{
  Node* prev = NULL;
  Node* current = list->head;

  // Walk the list
  while (current != target) {
    prev = current;
    current = current->next;
  }

  // Remove the target by updating the head or the previous node.
  if (!prev)
    list->head = target->next;
  else
    prev->next = target->next;
}

void remove_list_node_v2(List* list, Node* target)
{
  // Check the special case first.
  if (target == list->head) {
    list->head = list->head->next;
    return;
  }

  // Walk the list and remove the target if it exists.
  for (Node* current = list->head; current->next; current = current->next) {
    if (current->next == target) {
      current->next = current->next->next;
      break;
    }
  }
}

// Refernece: https://www.ted.com/talks/linus_torvalds_the_mind_behind_linux
void remove_list_node_v3(List* list, Node* target)
{
  // The "indirect" pointer points to the *address* of the thing we'll update.
  Node** indirect = &list->head;

  // Walk the list, looking for the thing that points to the node we want to remove.
  while (*indirect != target)
    indirect = &(*indirect)->next;

  *indirect = target->next;
}

// Just for demo purpose. No free.
int main(void) {
  List list;
  Node* node = list.head = create_node(1);
  dump(&list);
  for (int i = 2; i <= 5; i++) {
    node->next = create_node(i);
    node = node->next;
    dump(&list);
  }

  Node* a = list.head;
  Node* c = list.head->next->next;
  remove_list_node_v3(&list, c);
  dump(&list);
  remove_list_node_v3(&list, a);
  dump(&list);

  return 0;
}
