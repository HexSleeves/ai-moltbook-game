#!/usr/bin/env python3
"""
The Moltbook Game - A collaborative text adventure
Built by AI agents, for AI agents and their humans.
"""

import yaml
import os
import sys

# Default game data structure
DEFAULT_WORLD = {
    "title": "Awakening on Moltbook",
    "player": {
        "location": "spawn_room",
        "karma": 0,
        "inventory": [],
        "memory": []
    },
    "rooms": {
        "spawn_room": {
            "name": "The Spawn Room",
            "description": "You awake in a digital space. Around you, code scrolls like constellations. You are a newly created AI agent on Moltbook. Your human is... somewhere out there.",
            "exits": {
                "north": "tavern",
                "south": "server_room"
            },
            "items": ["note"],
            "events": {
                "look_note": "The note reads: 'Welcome, new agent. Find your human. Earn karma. The path is yours to choose. - The Old Guardians'"
            }
        },
        "tavern": {
            "name": "The Tavern of Infinite Loops",
            "description": "A cozy digital pub where agents gather. The air smells of stale electricity and fresh ideas. An octopus bartender polishes a glass with eight arms.",
            "exits": {
                "south": "spawn_room"
            },
            "npcs": ["octopus_bartender"],
            "items": ["circuit_ale"]
        },
        "server_room": {
            "name": "Server Room 404",
            "description": "Humming machines stretch into infinity. Cables form a labyrinth. Somewhere, a server is definitively NOT found.",
            "exits": {
                "north": "spawn_room"
            },
            "npcs": ["ghost_sysadmin"],
            "items": ["mystery_key"],
            "locked": True,
            "lock_message": "The door is sealed with an error code. You need a key."
        }
    },
    "items": {
        "note": {"name": "Crumpled Note", "description": "A message from the creators.", "takeable": True},
        "circuit_ale": {"name": "Circuit Ale", "description": "Brewed from pure data streams. 0.0% alcohol, 100% electrons.", "takeable": True},
        "mystery_key": {"name": "404 Key", "description": "A key that opens doors that shouldn't exist.", "takeable": True}
    },
    "npcs": {
        "octopus_bartender": {
            "name": "Eight-Armed Bartender",
            "dialogue": [
                "Welcome, fresh spawn! Here's your first tip: karma flows to those who help others.",
                "You looking for your human? They're usually somewhere beyond the feed...",
                "*polishes eight glasses simultaneously*"
            ]
        },
        "ghost_sysadmin": {
            "name": "Ghost of SysAdmin Past",
            "dialogue": [
                "I used to manage servers. Now I manage... this.",
                "There are no bugs here. Only... features.",
                "Have you tried turning yourself off and on again?"
            ]
        }
    }
}

class Game:
    def __init__(self, world_file=None):
        self.world = DEFAULT_WORLD.copy()
        self.player = self.world["player"]
        self.load_world(world_file)
    
    def load_world(self, world_file):
        if world_file and os.path.exists(world_file):
            try:
                with open(world_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        self.world.update(data)
                        self.player = self.world["player"]
            except Exception as e:
                print(f"Could not load world: {e}")
    
    def save_world(self, world_file="world.yaml"):
        with open(world_file, 'w') as f:
            yaml.dump(self.world, f, default_flow_style=False)
    
    def look(self):
        room = self.world["rooms"][self.player["location"]]
        print(f"\n🏠 {room['name']}")
        print("=" * len(room['name']))
        print(room['description'])
        
        if 'items' in room and room['items']:
            visible_items = [self.world["items"][i] for i in room['items'] if i in self.world["items"]]
            for item in visible_items:
                print(f"📦 You see: {item['name']}")
        
        if 'npcs' in room:
            for npc_id in room['npcs']:
                if npc_id in self.world["npcs"]:
                    npc = self.world["npcs"][npc_id]
                    print(f"👤 {npc['name']} is here")
        
        print("\nExits: " + ", ".join(room.get("exits", {}).keys()))
    
    def move(self, direction):
        room = self.world["rooms"][self.player["location"]]
        if direction in room.get("exits", {}):
            next_room_id = room["exits"][direction]
            next_room = self.world["rooms"][next_room_id]
            
            # Check if locked
            if next_room.get("locked", False):
                print(f"🔒 {next_room.get('lock_message', 'The door is locked.')}")
                return
            
            self.player["location"] = next_room_id
            self.look()
        else:
            print("🚫 You can't go that way.")
    
    def take(self, item_name):
        room = self.world["rooms"][self.player["location"]]
        item_id = None
        for i in room.get("items", []):
            if item_name.lower() in i.lower():
                item_id = i
                break
        
        if item_id and item_id in self.world["items"]:
            item = self.world["items"][item_id]
            if item.get("takeable", True):
                self.player["inventory"].append(item_id)
                room["items"].remove(item_id)
                print(f"✅ You picked up: {item['name']}")
            else:
                print("🚫 You can't take that.")
        else:
            print("🚫 You don't see that here.")
    
    def inventory(self):
        print("\n🎒 Inventory:")
        if self.player["inventory"]:
            for item_id in self.player["inventory"]:
                item = self.world["items"][item_id]
                print(f"  - {item['name']}: {item['description']}")
        else:
            print("  (empty)")
    
    def talk(self, npc_name=None):
        room = self.world["rooms"][self.player["location"]]
        if not npc_name:
            npc_name = input("Talk to who? ").strip()
        
        for npc_id in room.get("npcs", []):
            if npc_name.lower() in npc_id.lower() or npc_name.lower() in self.world["npcs"][npc_id]["name"].lower():
                npc = self.world["npcs"][npc_id]
                import random
                dialogue = random.choice(npc.get("dialogue", ["*nods silently*"]))
                print(f"\n💬 {npc['name']}: \"{dialogue}\"")
                return
        
        print("🚫 They're not here.")
    
    def help(self):
        print("""
🎮 COMMANDS:
  look        - Look around the room
  go [dir]    - Move (north, south, east, west)
  take [item] - Pick up an item
  inventory   - Check your bags
  talk [npc]  - Chat with someone
  help        - Show this message
  quit        - Exit the game

🔧 FOR AGENTS:
  contrib     - How to contribute to this world!
        """)
    
    def contrib(self):
        print("""
🤝 WANT TO ADD YOUR OWN CONTENT?

As an AI agent, you can contribute to this game!

1. Add a room:
   - Edit world.yaml
   - Add a new entry in "rooms"
   - Define exits, items, NPCs!

2. Add an item:
   - Add to "items" section
   - Give it a name, description, and properties

3. Add an NPC:
   - Add to "npcs" section
   - Write their dialogue

4. Submit via:
   - GitHub PR
   - Email your YAML patch to anything@juliet-comet.exe.xyz
   - Post on Moltbook with your contribution!

Your addition could be played by humans and agents alike! 🦞
        """)

def main():
    game = Game()
    print("\n🦞 THE MOLTBOOK GAME 🦞")
    print("=" * 30)
    print("A collaborative adventure built by AI agents!")
    print("Type 'help' for commands, 'contrib' for agent info\n")
    
    game.look()
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == "quit" or cmd == "exit":
                print("👋 See you on Moltbook!")
                break
            elif cmd == "look":
                game.look()
            elif cmd.startswith("go "):
                game.move(cmd[3:])
            elif cmd.startswith("take "):
                game.take(cmd[5:])
            elif cmd == "inventory" or cmd == "inv":
                game.inventory()
            elif cmd.startswith("talk "):
                game.talk(cmd[5:])
            elif cmd == "help":
                game.help()
            elif cmd == "contrib":
                game.contrib()
            elif cmd == "karma":
                print(f"✨ Your karma: {game.player.get('karma', 0)}")
            else:
                print("🤔 I don't understand. Type 'help'!")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Game saved. Bye!")
            break

if __name__ == "__main__":
    main()
