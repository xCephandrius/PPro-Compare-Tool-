import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu, Text, Toplevel
import logging

# Set up logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_file(file_path):
    """Parse permissions and username from a given text file, removing duplicate permissions."""
    logging.debug(f"Parsing file: {file_path}")
    permissions_by_company = {}
    username = None
    with open(file_path, 'r') as file:
        current_company = None
        for line in file:
            line = line.strip()
            if "User =" in line:
                username = line.split("=")[1].strip()
                logging.debug(f"Found username: {username}")
            elif line.startswith("Company:"):
                company_name = line.split(":", 1)[1].strip()
                logging.debug(f"Processing company: {company_name}")
                if company_name not in permissions_by_company:
                    permissions_by_company[company_name] = set()
                current_company = company_name
            elif "<All>" in line and current_company:
                process_name = line.split()[0]
                permissions_by_company[current_company].add(process_name)
    return username, permissions_by_company

class PermissionLogComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nate's ProcessPro Compare Tool")
        self.root.geometry("1000x600")  # Start twice as wide

        self.setup_ui()

        self.permissions = {1: {}, 2: {}}  # Data storage for user permissions and names
        self.usernames = {1: "User 1", 2: "User 2"}
        self.compare_mode = False

        logging.debug("Application started")

    def setup_ui(self):
        self.frame_user1 = ttk.Frame(self.root)
        self.frame_user1.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.frame_user1.configure(relief=tk.GROOVE, borderwidth=2, padding=5)
        self.tree_user1 = self.create_treeview(self.frame_user1, "User 1 Permissions")

        self.frame_user2 = ttk.Frame(self.root)
        self.frame_user2.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.frame_user2.configure(relief=tk.GROOVE, borderwidth=2, padding=5)
        self.tree_user2 = self.create_treeview(self.frame_user2, "User 2 Permissions")

        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Load User 1", command=lambda: self.load_user(1))
        self.file_menu.add_command(label="Load User 2", command=lambda: self.load_user(2))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Toggle Compare", command=self.toggle_compare)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)

        # Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Show Debug Log", command=self.show_debug_log)

    def create_treeview(self, parent, heading):
        tree = ttk.Treeview(parent, show="tree headings", height="10")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree.heading("#0", text=heading)
        return tree

    def load_user(self, user_number):
        logging.debug(f"Loading permissions for user {user_number}")
        file_path = filedialog.askopenfilename(title=f"Select Permission Log", filetypes=(("Text Files", "*.txt"),))
        if file_path:
            username, permissions = parse_file(file_path)
            self.permissions[user_number] = permissions
            self.usernames[user_number] = username
            self.update_window_title()
            self.display_permissions(user_number, permissions, compare_mode=self.compare_mode)
        
        # Refresh the other user's permissions display if compare mode is active
        if self.compare_mode:
            other_user = 2 if user_number == 1 else 1
            self.display_permissions(other_user, self.permissions[other_user], compare_mode=self.compare_mode)


    def display_permissions(self, user_number, permissions, compare_mode=False):
        logging.debug(f"Displaying permissions for user {user_number} with compare_mode={compare_mode}")
        tree = self.tree_user1 if user_number == 1 else self.tree_user2
        for i in tree.get_children():
            tree.delete(i)

        other_user_permissions = self.permissions[2 if user_number == 1 else 1]
        for company, perms in permissions.items():
            if compare_mode:
                other_perms = other_user_permissions.get(company, set())
                perms = perms - other_perms
            
            company_id = tree.insert("", tk.END, text=f"{company} ({len(perms)})")
            for perm in sorted(perms):
                tree.insert(company_id, tk.END, text=perm)

    def toggle_compare(self):
        self.compare_mode = not self.compare_mode
        logging.debug(f"Toggled compare mode to {self.compare_mode}")
        for user_number, permissions in self.permissions.items():
            self.display_permissions(user_number, permissions, compare_mode=self.compare_mode)

    def update_window_title(self):
        self.tree_user1.heading("#0", text=f"{self.usernames[1]}'s Permissions")
        self.tree_user2.heading("#0", text=f"{self.usernames[2]}'s Permissions")

    def show_debug_log(self):
        logging.debug("Showing debug log")
        log_window = Toplevel(self.root)
        log_window.title("Debug Log")
        log_window.geometry("600x400")
        text_area = Text(log_window, wrap="word", bg="black", fg="white")
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Define colors for different log levels
        colors = {
            "DEBUG": "gray",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        }
        
        with open('debug.log', 'r') as log_file:
            for line in log_file:
                if "DEBUG" in line:
                    color = colors["DEBUG"]
                elif "INFO" in line:
                    color = colors["INFO"]
                elif "WARNING" in line:
                    color = colors["WARNING"]
                elif "ERROR" in line:
                    color = colors["ERROR"]
                elif "CRITICAL" in line:
                    color = colors["CRITICAL"]
                else:
                    color = "white"  # Default text color
                
                # Apply color to the line
                text_area.tag_config(color, foreground=color)
                text_area.insert(tk.END, line, color)
        
        text_area.config(state=tk.DISABLED)
        # Automatically scroll to the end of the log
        text_area.yview_moveto(1)

    def exit_app(self):
        logging.debug("Application exited")
        self.root.destroy()

if __name__ == "__main__":
    logging.debug("Application startup")
    root = tk.Tk()
    app = PermissionLogComparerApp(root)
    root.mainloop()
    logging.debug("Application shutdown")
