# Recreation of the WorldGen/Dialogues/D31.xml file from release a0819
# as a Tachyon Diagen script

# Shorthand for adding tutorial skip
def skippable(message):
    return Choice(message, [
        [],
        [
            Response("I would like to skip the tutorial."),
            Goto("Skip"),
        ],
    ])

# Shorthand for hyperdrive test
def hyperdrive_condition(state, model, player):
    return Condition(
        f"SHIP_CARGO_{state}", cargo_type="SHIP_SYSTEM", system_model=model, target_player=player, qty=1
    )

dialogues = {
    "TUTORIAL": [
        Choice("[ACTION]You see a Human in a torn and burned space suit, with some blood stains...", [
            #[
            #    Response("Run test event with player as target"),
            #
            #    "Executing test event, targeted at player!",
            #    Event("RUN_TEST", "PLAYER"),
            #    Response("Thanks"),
            #],
            #[
            #    Response("Run test event with npc as target"),
            #
            #    "Executing test event, targeted at npc!",
            #    Event("RUN_TEST", "NPC"),
            #    Response("Thanks"),
            #],
            [
                Condition("SERVER_VARIABLE_ABSENT", var_name="TUTORIALS_STARTED", var_value=1),

                skippable("Thank God! I thought I was the only survivor!"),
                Event("SS31_STOP_CALLING_HELP", "PLAYER"),
                Response("Who are you?"),
                skippable("I'm [NPC_NAME], the captain of this station...  Well what's left of it..."),
                Response("What happened here?"),
                skippable("You're [PLAYER_NAME] right? Don't you remember anything?"),
                Response("No. I don't!"),
                skippable("Damn. The clone replication system must have been damaged."),
                skippable("This is the D31 Science station. You are posted here as one of the guards."),
                skippable("We were attacked by pirates, and they have stolen one of our prototype ships!"),
                skippable("We need to report this to the Unity Science Centre. ASAP!"),
                skippable("Problem is that the pirates have taken out our communications system."),
                skippable("We need to think of a way to get the message to the USC."),
                Response("How can I help?"),

                Choice("Please repair all systems you can.", [
                    [
                        Response("How do I repair stuff, or put out fires?"),
                        "Just walk into the room with a damaged system and it will auto repair.",
                        "Same thing with the hull breach, just stand on top of it, and it will auto repair.",
                        "To put out fire just stand on top of it and it will auto extinguish.",
                    ],
                    [
                        Response("I'm on it"),
                    ],
                ]),
                "Thanks. Speak to me when you're done.",
                Event("START_TUTORIALS", "PLAYER"),
                Event("START_REPAIR_TUTORIAL", "PLAYER"),
                End,

                Label("Skip"),
                Choice("Are you sure?", [
                    [
                        Response("I changed my mind.  Teach me oh great master!"),
                        Goto("M0"),
                    ],
                    [
                        Response("Yes.  let's go!"),

                        "Ok. Don't forget to power up the systems!",
                        Event("SET_PLAYER_OWNER", "PLAYER"),
                        Event("SPAWN_USC", "PLAYER"),
                        Event("MAKE_USC_SECTOR_EXPLORED", "PLAYER"),
                        Event("SKIP_TUTORIAL0", "NPC"),
                        Event("SKIP_TUTORIAL", "PLAYER"),
                        Event("SKIP_TUTORIAL2", "NPC"),
                        Goto("HJ"),
                    ],
                ]),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="REPAIR_TUTORIAL_STARTED", var_value=1),

                Choice("Oh it's you [PLAYER_NAME].  Have you already finished all the repairs?", [
                    [
                        Response("I've fixed all the systems and breaches I could reach."),
                    ] + [
                        Condition("SHIP_SYSTEM_PRESENT", system_type=system, active_system=1, qty=qty)
                        for system, qty in [
                            ("OXYGEN", 2), ("CAPACITOR", 4), ("REPAIR", 1), ("LASER_WEAPONS", 1), ("SHIELDS", 1),
                        ]
                    ] + [

                        "Excellent! And I have a plan how we can get that message to USC!",
                        Response("How?"),
                        "Our second prototype ship, it's badly damaged but still operational.",
                        "I want you to go and repair it. And I suggest you start with the REACTOR.",
                        "Also keep an eye on your oxygen level. Because that ship probably has no O2.",
                        "After you have repaired it, I want you to take control of it and talk to me again.",
                        "You can use the Comms on the ship if you want.",
                        Choice("Meanwhile I want to check something in the Sensors room.", [
                            [Response("OK.")],
                            [
                                Response("How do I claim a ship for my self?"),
                                Goto("CL_HOWTO"),
                            ],
                        ]),
                        Event("STOP_REPAIR_TUTORIAL", "PLAYER"),
                        Event("START_CLAIM_TUTORIAL", "PLAYER"),
                        Event("SS31_GO_TO_SENSORS", "PLAYER"),
                    ],
                    [
                        Response("No, not yet."),
                        AnyCondition("1"),
                    ] + [
                        Condition("SHIP_SYSTEM_ABSENT", system_type=system, active_system=1, qty=qty)
                        for system, qty in [
                            ("OXYGEN", 2), ("CAPACITOR", 2), ("REPAIR", 1), ("LASER_WEAPONS", 1),
                        ]
                    ] + [

                        "Please speak to me again when you're done fixing.",
                        Response("Ok."),
                    ],
                    [
                        Response("Can you please remind me how to do repairs?"),

                        "Just walk into the room with a damaged system.",
                        "To put out fire just stand on top of it",
                        Response("Thanks!"),
                    ],
                ]),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="CLAIM_TUTORIAL_STARTED", var_value=1),

                Choice("Hello [PLAYER_NAME].  Are you now a captain or crew on a ship?", [
                    [
                        Response("Yes, I am now port of a ship crew."),
                        Condition("SHIP_SYSTEM_PRESENT", target_player=1, system_type="PILOTING", qty=1),

                        "Good.  Let's see now... ",
                        "The Second prototype ship is near death. You'll never be able to reach USC like this.",
                        "Not to mention that the Hyper drive is missing completely!",
                        Response("What do we do then?"),
                        "Well at least the engine is intact. ",
                        "Let me run a sector scan with the Sensors.",
                        "Maybe there's an HD in one of the debris fields.",
                        "Hmm... No luck.  But I see there are several broken ones.",
                        "Perhaps we can assemble a working one from all the broken pieces.",
                        "I see there's a Tachyon Stabilizer, Accelerator and Chamber floating in space.",
                        "I want you to pilot the second prototype ship and recover these parts for me.",
                        "With them I think I will be able to assemble a new Hyper drive for you.",

                        Choice("Look for me in the LASER WEAPON room when you are done.", [
                            [Response("Great. I'll get right on it.")],
                            [
                                Response("Can you remind me how to pilot a ship within the sector?"),
                                Goto("LJ_HOWTO"),
                            ],
                            [
                                Response("How do I pick up debris and cargo in space?"),
                                Goto("PICK_HOWTO"),
                            ],
                            [
                                Response("How do I find items in space?"),
                                Goto("FIND_HOWTO"),
                            ],
                        ]),
                        Event("STOP_CLAIM_TUTORIAL", "PLAYER"),
                        Event("START_LJ_TUTORIAL", "PLAYER"),
                        Event("SPAWN_HD_PARTS", "PLAYER"),
                        Event("SS31_STOP_GO_TO_SENSORS", "PLAYER"),
                        Event("SS31_GO_TO_LASER", "PLAYER"),
                    ],
                    [
                        Response("No, not yet"),
                        Condition("SHIP_SYSTEM_ABSENT", target_player=1, system_type="PILOTING", qty=1),

                        "Well, what are you waiting for?  Go do it!",
                        Response("OK. I'm on it"),
                    ],
                    [
                        Response("Please remind me how to claim a ship or add crew."),

                        Label("CL_HOWTO"),
                        "You need to go to the PILOTING room, and open the system interface.",
                        "To open the system interface press SPACE.  There open the CREW page.",
                        "If a ship has no owner/captain, then there will be a CLAIM button.",
                        "When you are the captain of the ship you can add more crew to it.",
                        "To do that - press the ADD CREW button and input the name.",
                        "When the crew member is not present in the sector it shows - NO DATA",
                        "That's pretty much it.",
                        Response("Thanks!"),
                    ],
                ]),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="LJ_TUTORIAL_STARTED", var_value=1),

                Choice("Hi [PLAYER_NAME].  Did you recover the Hyper Drive parts?", [
                    [
                        Response("Yes. All Hyper Drive parts are transferred to the station."),
                        hyperdrive_condition("PRESENT", "TACSTAB", 0),
                        hyperdrive_condition("PRESENT", "TACCHAMB", 0),
                        hyperdrive_condition("PRESENT", "TACACC", 0),

                        "Great work [PLAYER_NAME]!  I will start assembling the new HD right away.",
                        "Meanwhile you can do some hull repairs for the second prototype ship.",
                        "On this station there's a repair system.",
                        "But you will need some scrap metal to use it.",
                        Response("Where can I get scrap?"),
                        "When a ship or an asteroid is blown up, there will be some scrap left.",
                        "I will uninstall the station's laser and send it to your ship, so you can use it.",
                        Choice("Install the laser, blow up asteroids and repair the ship.", [
                            [Response("Will do.")],
                            [
                                Response("Wait, how do I install or uninstall systems on the ship?"),
                                Goto("INST_HOWTO"),
                            ],
                            [
                                Response("Wait, I don't know how to use weapons!"),
                                Goto("SHOOT_HOWTO"),
                            ],
                        ]),
                        Event("STOP_LJ_TUTORIAL", "PLAYER"),
                        Event("START_INST_TUTORIAL", "PLAYER"),
                        Event("SPAWN_ASTEROIDS", "PLAYER"),
                        Event("REMOVE_STATION_LASER", "NPC"),
                        Event("ADD_LASER_TO_PLAYER", "PLAYER"),
                        Event("SS31_GO_TO_SENSORS", "PLAYER"),
                        Event("SS31_STOP_GO_TO_LASER", "PLAYER"),
                    ],
                    [
                        Response("Yes, I have the Tachyon Stabilizer on my ship."),
                        hyperdrive_condition("PRESENT", "TACSTAB", 1),

                        Label("DROP_HD"),
                        Choice("Excellent! Please drop it off into the station.", [
                            [Response("OK."), End],
                            [Response("How do I do that?")],
                        ]),

                        "Open the PILOTING system interface and go to the CARGO page.",
                        "There you will see all your ship's cargo.  Click the one you want to jettison,",
                        "then select a direction in which you want to jettison the cargo box.",
                        "To do that you need to click the button that looks like a direction arrow.",
                        "It is located near the JET. CARGO button.  When you click it, it will change the direction.",
                        "So if the station is below your ship, then select direction DOWN.",
                        "Then press the JET. CARGO button to throw the cargo box out and it will fly in that direction.",
                        Response("OK. Thanks!"),
                    ],
                    [
                        Response("Yes, I have the Tachyon Chamber on my ship."),
                        hyperdrive_condition("PRESENT", "TACCHAMB", 1),
                        Goto("DROP_HD"),
                    ],
                    [
                        Response("Yes, I have the Tachyon Accelerator on my ship."),
                        hyperdrive_condition("PRESENT", "TACACC", 1),
                        Goto("DROP_HD"),
                    ],
                    [
                        Response("No, not yet."),
                        hyperdrive_condition("ABSENT", "TACSTAB", 1),
                        hyperdrive_condition("ABSENT", "TACCHAMB", 1),
                        hyperdrive_condition("ABSENT", "TACACC", 1),

                        "Please don't waste any time. It is of the essence.",
                    ],
                    [
                        Response("Can you remind me how to pilot a ship within the sector?"),

                        Label("LJ_HOWTO"),
                        "Open the PILOTING system interface and go to SECTOR MAP page.",
                        "Or go to the ENGINES room and open the ENGINES system interface.",
                        "On the bottom you will see the Engines energy meter and power bars.",
                        "Left click on the power bars to divert some power to the engines.",
                        "Right click to de-power. Once the energy meter is full - you can jump.",
                        "Left click somewhere on the radar map where you want to move your ship.",
                        "Then press the JUMP button.  And away you go!",
                        "Don't forget to upgrade your engines to be able to charge them faster.",
                        Response("Thanks!"),
                    ],
                    [
                        Response("How do I pick up debris and cargo in space?"),

                        Label("PICK_HOWTO"),
                        "You can jump on top of them with your ship.",
                        "Or you can fly out in space through an airlock, approach the debris, ",
                        "and then press the debris button (SPACE) to grab it. Then haul it back to the ship.",
                        "Also most debris will be attracted to the ship if they are close enough.",
                        Response("Thanks."),
                    ],
                    [
                        Response("How do I find items in space?"),

                        Label("FIND_HOWTO"),
                        "On the sector map debris and cargo boxes are shown as orange dots.",
                        "And on the target map the cargo box looks like a box rather some scrap metal.",
                        Response("Thanks."),
                    ],

                ]),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="INST_TUTORIAL_STARTED", var_value=1),
                Choice("[PLAYER_NAME], Have you repaired the ship's hull?", [
                    [
                        Response("No, not yet."),
                        Condition("SHIP_HULL_ABSENT", target_player=1, qty=50),

                        "Please hurry up and repair the ship.",
                        Response("I'm on it."),
                    ],
                    [
                        Response("Yes, the ship is fully repaired."),
                        Condition("SHIP_HULL_PRESENT", target_player=1, qty=50),

                        "Perfect timing [PLAYER_NAME]!",
                        "Sensors have detected an incomming ship signature.",
                        "It must be the pirates' salvage team, comming to finish us up!",
                        "Use the laser I gave you, and blow them to space dust!",
                        "Speak to me again when the pirates are dealt with.",
                        Event("STOP_INST_TUTORIAL", "PLAYER"),
                        Event("START_FIGHT_TUTORIAL", "PLAYER"),
                        Event("SPAWN_TUT_PIRATE", "PLAYER"),
                        Response("I'm on it!"),
                    ],
                    [
                        Response("Please remind me how to install and uninstall systems"),

                        Label("INST_HOWTO"),
                        "To uninstall a system - Open the PILOTING interface and go to the SYSTEMS page",
                        "There you will see the layout of the ship.  Click on a system you want to unsinstall,",
                        "then click the UNINSTALL button on the bottom left.  And it will be moved to your cargo hold.",
                        "If your cargo hold is full though, the system will be jettisoned into outer space.",
                        "Be careful, when you uninstall a system, it looses any upgrades it had.",
                        "And some systems can't be uninstalled without breaking and loosing them.",
                        Response("OK. Got it."),

                        "To install a system - Open the PILOTING interface and go to the CARGO page",
                        "There you will see all the cargo that you have.  Click on the system that you want to install,",
                        "Then click on the INSTALL button on the bottom left.",
                        "A window will appear, where you can select the place to install the system.",
                        "Click the top left corner of any room to install a system in it.",
                        "On the bottom of the ship layout window there's a button that rotates the system.",
                        Response("OK. Thanks."),
                    ],
                    [
                        Response("Can you tell me how to shoot weapons?"),
                        Goto("SHOOT_HOWTO"),
                    ],

                ]),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="FIGHT_TUTORIAL_STARTED", var_value=1),
                Condition("SECTOR_SHIPS_PRESENT", qty=3),

                Choice("What are you still doing here?!  Go blow up that pirate!", [
                    [Response("I'm working on it.")],
                    [
                        Response("I forgot how to shoot!"),

                        Label("SHOOT_HOWTO"),
                        "There are two ways to shoot your weapons,",
                        "First way is to man the weapon itself:",
                        "To do that you need to go into the room where the weapon is installed,",
                        "and open the system interface.",
                        "There you will see 2 screens: Radar screen and Target screen.",
                        "On the Radar screen you can see all the ships and space ojects in the sector.",
                        "On the target screen you see the ships in detail, with their systems and stats.",
                        "To shoot, you need to power the weapon, let it charge to full,",
                        "Then click a spot on the target map, and a croshair will appear there.",
                        "Then you just press the FIRE button and it's done.",
                        "You can see the projectiles traveling on the Radar map.",
                        Response("And the second way?"),
                        "Second way is to man the WEAPONS CONTROL system.",
                        "Go to the WEAPONS CONTROL room and open the system interface.",
                        "It is almost the same as the WEAPON system interface,",
                        "but from here you can shoot any weapon on the ship.",
                        "Under the Radar map screen you will see a bar with all available weapons.",
                        "To shoot you first need to select which weapon you want to aim.",
                        "Click on the icon of the weapon you need and then select the target.",
                        "To fire each weapon individually you can press their own small FIRE button.",
                        "To fire all ready weapons at the same time, press the FRIE ALL button.",
                        Response("Thanks."),
                    ],
                ]),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="FIGHT_TUTORIAL_STARTED", var_value=1),
                Condition("SECTOR_SHIPS_ABSENT", qty=3),

                "Great work destroying those pirates [PLAYER_NAME]!",
                Response("Yeah, that wasn't so hard."),

                Choice("I've finished assembling the new HYPER DRIVE for you.", [
                    [
                        AnyCondition("1"),
                        Condition("SERVER_VARIABLE_PRESENT", var_name="PLAYER_CREW_SPAWNED", var_value=1),
                        Condition("SECTOR_PLAYERS_PRESENT", qty=3),
                    ],
                    [
                        Condition("SERVER_VARIABLE_ABSENT", var_name="PLAYER_CREW_SPAWNED", var_value=1),
                        Condition("SECTOR_PLAYERS_ABESNT", qty=3),
                        Condition("SECTOR_PLAYERS_PRESENT", qty=2),

                        "I've also managed to assemble some repair droids for you.",
                        Event("SPAWN_NPC_CREW_2", "PLAYER"),
                        Response("That's even better!"),
                    ],
                    [
                        Condition("SERVER_VARIABLE_ABSENT", var_name="PLAYER_CREW_SPAWNED", var_value=1),
                        Condition("SECTOR_PLAYERS_ABESNT", qty=2),

                        "I've also managed to assemble some repair droids for you.",
                        Event("SPAWN_NPC_CREW_3", "PLAYER"),
                        Response("That's even better!"),
                    ],
                ]),
                Response("That's great news!"),
                Choice("I will send the new Hyperdrive to the your ship's cargo hold.", [
                    [
                        Condition("SERVER_VARIABLE_ABSENT", var_name="USC_SPAWNED", var_value=1),

                        "Install the Hyper Drive and travel to the USC station in sector [SECTOR].",
                        Event("SPAWN_USC", "PLAYER"),
                        Event("MAKE_USC_SECTOR_EXPLORED", "PLAYER"),
                    ],
                    [
                        Condition("SERVER_VARIABLE_PRESENT", var_name="USC_SPAWNED", var_value=1),

                        "Install the Hyper Drive and travel to the USC station in sector VAR(USC_SECTOR).",
                    ],
                ]),
                Response("Thanks"),
                Choice("There you will need to find Dr. Darius Graydon, and tell him what happened here.", [
                    [Response("I will get right on it.")],
                    [
                        Response("Can you tell me how to do Hyper jumps?"),
                        Goto("HJ_HOWTO"),
                    ],
                ]),
                Event("ADD_HD_TO_PLAYER", "PLAYER"),
                Event("REMOVE_D31_SAFEZONE", "NPC"),
                Event("STOP_FIGHT_TUTORIAL", "PLAYER"),
                Event("START_HJ_TUTORIAL", "PLAYER"),
            ],
            [
                Condition("SERVER_VARIABLE_PRESENT", var_name="HJ_TUTORIAL_STARTED", var_value=1),

                Label("HJ"),
                Choice("Please find Dr. Darius Graydon, at USC in sector VAR(USC_SECTOR)", [
                    [Response("I'm on my way.")],
                    [
                        Response("Please remind me ho to do Hyper jumps."),

                        Label("HJ_HOWTO"),
                        "To do a hyper jump, open the PILOTING interface and go to the STAR MAP page.",
                        "There you can see all the stars and empy space sectors.",
                        "The ship icon will indicate in which sector you are located right now.",
                        "You can see the glowing circles indicating what sectors you can reach.",
                        "The range depends on your Hyper Drive power and level and the class of your ship.",
                        "On the bottom of the screen you can see the Hyper Drive power bars and energy level.",
                        "Add some power to the Hyper Drive and see the energy bar filling up.",
                        "As the Hyper drive charges more energy, you will see glowing circles getting blue color.",
                        "Blue circles indicate the sectors that you can jump to with current stored energy.",
                        "Select a destination sector from one of the blue circles, then click the SET TARGET button.",
                        "Then press the HYPER JUMP button, and away you go, into the hyper space.",
                        Response("Thanks!"),
                    ],
                ]),
            ],
        ]),
    ],
}
