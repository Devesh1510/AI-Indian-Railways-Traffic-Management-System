class RailwayState:
    def __init__(self):
        # -------------------------------------------------
        # TRAIN STATE
        # -------------------------------------------------
        # Each train now has a controlling_signal.
        # Movement checks the REAL signal state below.
        self.trains = [
            {
                "train_id": "TRAIN_101",
                "position": 15,
                "speed": 45,
                "platform": "P1",
                "route": "A",
                "status": "RUNNING",
                "signal": "GREEN",
                "controlling_signal": "S1",
                "delay": 3,
            },
            {
                "train_id": "TRAIN_102",
                "position": 32,
                "speed": 35,
                "platform": "P2",
                "route": "A",
                "status": "RUNNING",
                "signal": "YELLOW",
                "controlling_signal": "S2",
                "delay": 5,
            },
            {
                "train_id": "TRAIN_103",
                "position": 48,
                "speed": 50,
                "platform": "P3",
                "route": "B",
                "status": "RUNNING",
                "signal": "GREEN",
                "controlling_signal": "S3",
                "delay": 0,
            },
            {
                "train_id": "TRAIN_104",
                "position": 61,
                "speed": 0,
                "platform": "P4",
                "route": "B",
                "status": "STOPPED",
                "signal": "RED",
                "controlling_signal": "S4",
                "delay": 8,
            },
            {
                "train_id": "TRAIN_105",
                "position": 24,
                "speed": 40,
                "platform": None,
                "route": "C",
                "status": "RUNNING",
                "signal": "GREEN",
                "controlling_signal": "S5",
                "delay": 2,
            },
            {
                "train_id": "TRAIN_106",
                "position": 72,
                "speed": 30,
                "platform": None,
                "route": "C",
                "status": "RUNNING",
                "signal": "DOUBLE YELLOW",
                "controlling_signal": "S6",
                "delay": 6,
            },
            {
                "train_id": "TRAIN_107",
                "position": 83,
                "speed": 0,
                "platform": None,
                "route": "A",
                "status": "STOPPED",
                "signal": "RED",
                "controlling_signal": "S7",
                "delay": 10,
            },
            {
                "train_id": "TRAIN_108",
                "position": 91,
                "speed": 40,
                "platform": None,
                "route": "B",
                "status": "RUNNING",
                "signal": "YELLOW",
                "controlling_signal": "S8",
                "delay": 1,
            },
        ]

        # -------------------------------------------------
        # SIGNAL STATE
        # -------------------------------------------------
        self.signals = [
            {
                "signal_id": "S1",
                "position": 10,
                "status": "GREEN",
                "mode": "AUTO",
            },
            {
                "signal_id": "S2",
                "position": 25,
                "status": "YELLOW",
                "mode": "AUTO",
            },
            {
                "signal_id": "S3",
                "position": 40,
                "status": "GREEN",
                "mode": "AUTO",
            },
            {
                "signal_id": "S4",
                "position": 55,
                "status": "RED",
                "mode": "AUTO",
            },
            {
                "signal_id": "S5",
                "position": 65,
                "status": "GREEN",
                "mode": "AUTO",
            },
            {
                "signal_id": "S6",
                "position": 70,
                "status": "DOUBLE YELLOW",
                "mode": "AUTO",
            },
            {
                "signal_id": "S7",
                "position": 80,
                "status": "RED",
                "mode": "AUTO",
            },
            {
                "signal_id": "S8",
                "position": 88,
                "status": "YELLOW",
                "mode": "AUTO",
            },
            {
                "signal_id": "S9",
                "position": 20,
                "status": "GREEN",
                "mode": "AUTO",
            },
            {
                "signal_id": "S10",
                "position": 35,
                "status": "GREEN",
                "mode": "AUTO",
            },
            {
                "signal_id": "S11",
                "position": 60,
                "status": "YELLOW",
                "mode": "AUTO",
            },
            {
                "signal_id": "S12",
                "position": 95,
                "status": "RED",
                "mode": "AUTO",
            },
        ]

        # -------------------------------------------------
        # PLATFORM STATE
        # -------------------------------------------------
        self.platforms = [
            {
                "platform_id": "P1",
                "occupied": True,
                "train_id": "TRAIN_101",
            },
            {
                "platform_id": "P2",
                "occupied": True,
                "train_id": "TRAIN_102",
            },
            {
                "platform_id": "P3",
                "occupied": True,
                "train_id": "TRAIN_103",
            },
            {
                "platform_id": "P4",
                "occupied": True,
                "train_id": "TRAIN_104",
            },
        ]

        self.simulation_running = True

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _get_signal(self, signal_id):
        for signal in self.signals:
            if signal["signal_id"] == signal_id:
                return signal
        return None

    def _get_train(self, train_id):
        for train in self.trains:
            if train["train_id"] == train_id:
                return train
        return None

    # =====================================================
    # TRAIN MOVEMENT
    # =====================================================

    def move_train(self, train_id):
        train = self._get_train(train_id)

        if train is None:
            return {
                "success": False,
                "message": f"Train {train_id} not found.",
            }

        signal_id = train["controlling_signal"]
        signal = self._get_signal(signal_id)

        if signal is None:
            return {
                "success": False,
                "message": (
                    f"Controlling signal {signal_id} "
                    f"for {train_id} was not found."
                ),
            }

        # IMPORTANT:
        # Always synchronize the train's displayed signal
        # with the actual controlling signal.
        train["signal"] = signal["status"]

        # -------------------------------------------------
        # SAFETY RULE
        # -------------------------------------------------
        # RED = train cannot move.
        # YELLOW / DOUBLE YELLOW / GREEN = train can move.
        allowed_signals = [
            "YELLOW",
            "DOUBLE YELLOW",
            "GREEN",
        ]

        if signal["status"] not in allowed_signals:
            train["speed"] = 0
            train["status"] = "STOPPED"

            return {
                "success": False,
                "train_id": train_id,
                "signal_id": signal_id,
                "signal": signal["status"],
                "position": train["position"],
                "status": "STOPPED",
                "message": (
                    f"{train_id} cannot move because "
                    f"{signal_id} is RED."
                ),
            }

        # -------------------------------------------------
        # MOVE TRAIN
        # -------------------------------------------------
        movement = max(1, train["speed"] / 20)

        train["position"] += movement

        # Prevent position from exceeding route length.
        if train["position"] >= 100:
            train["position"] = 100
            train["speed"] = 0
            train["status"] = "ARRIVED"

            return {
                "success": True,
                "train_id": train_id,
                "signal_id": signal_id,
                "signal": signal["status"],
                "position": train["position"],
                "status": "ARRIVED",
                "message": f"{train_id} has arrived.",
            }

        train["status"] = "RUNNING"

        return {
            "success": True,
            "train_id": train_id,
            "signal_id": signal_id,
            "signal": signal["status"],
            "position": round(train["position"], 2),
            "speed": train["speed"],
            "status": train["status"],
            "message": (
                f"{train_id} moved successfully "
                f"under {signal['status']} signal."
            ),
        }

    # =====================================================
    # GET TRAIN
    # =====================================================

    def get_train(self, train_id):
        return self._get_train(train_id)

    # =====================================================
    # MANUAL SIGNAL OVERRIDE
    # =====================================================

    def set_signal(self, signal_id, status):
        allowed_statuses = [
            "RED",
            "DOUBLE YELLOW",
            "YELLOW",
            "GREEN",
        ]

        if status not in allowed_statuses:
            return {
                "success": False,
                "message": (
                    "Invalid signal status. "
                    "Use RED, DOUBLE YELLOW, "
                    "YELLOW or GREEN."
                ),
            }

        signal = self._get_signal(signal_id)

        if signal is None:
            return {
                "success": False,
                "message": f"Signal {signal_id} not found.",
            }

        # Change actual signal.
        signal["status"] = status
        signal["mode"] = "MANUAL"

        # Synchronize every train controlled by this signal.
        affected_trains = []

        for train in self.trains:
            if train["controlling_signal"] == signal_id:
                train["signal"] = status

                # RED immediately stops the train.
                if status == "RED":
                    train["speed"] = 0
                    train["status"] = "STOPPED"

                affected_trains.append(train["train_id"])

        return {
            "success": True,
            "signal_id": signal_id,
            "status": status,
            "mode": "MANUAL",
            "affected_trains": affected_trains,
            "message": (
                f"{signal_id} changed to {status} "
                f"under manual control."
            ),
        }

    # =====================================================
    # MANUAL PLATFORM OVERRIDE
    # =====================================================

    def set_train_platform(self, train_id, platform_id):
        train = self._get_train(train_id)

        if train is None:
            return {
                "success": False,
                "message": f"Train {train_id} not found.",
            }

        platform = None

        for item in self.platforms:
            if item["platform_id"] == platform_id:
                platform = item
                break

        if platform is None:
            return {
                "success": False,
                "message": f"Platform {platform_id} not found.",
            }

        # Clear previous platform.
        if train["platform"]:
            for item in self.platforms:
                if item["platform_id"] == train["platform"]:
                    item["occupied"] = False
                    item["train_id"] = None

        # Assign new platform.
        train["platform"] = platform_id

        platform["occupied"] = True
        platform["train_id"] = train_id

        return {
            "success": True,
            "train_id": train_id,
            "platform_id": platform_id,
            "message": (
                f"{train_id} moved to platform "
                f"{platform_id}."
            ),
        }

    
    # =====================================================
    # AUTOMATIC SIMULATION
    # =====================================================

    def simulation_tick(self):
        """
        Move every train that is allowed to move.

        RED:
            Train remains stopped.

        YELLOW / DOUBLE YELLOW / GREEN:
            Train moves according to its speed.
        """

        results = []

        for train in self.trains:
            result = self.move_train(train["train_id"])
            results.append(result)

        return {
            "success": True,
            "simulation_running": self.simulation_running,
            "results": results,
        }

    def start_simulation(self):
        self.simulation_running = True

        return {
            "success": True,
            "simulation_running": True,
            "message": "Railway simulation started.",
        }

    def stop_simulation(self):
        self.simulation_running = False

        # Stop active trains when simulation is paused.
        for train in self.trains:
            if train["status"] == "RUNNING":
                train["status"] = "STOPPED"

        return {
            "success": True,
            "simulation_running": False,
            "message": "Railway simulation stopped.",
        }

    # =====================================================
    # DASHBOARD STATE
    # =====================================================

    def get_dashboard_state(self):
        occupied_platforms = sum(
            1 for platform in self.platforms
            if platform["occupied"]
        )

        return {
            "simulation_running": self.simulation_running,
            "active_trains": len(self.trains),
            "signals": len(self.signals),
            "occupied_platforms": occupied_platforms,
            "total_platforms": len(self.platforms),
            "trains": self.trains,
            "signals_state": self.signals,
            "platforms": self.platforms,
        }

    # =====================================================
    # FULL STATE
    # =====================================================

    def get_full_state(self):
        return {
            "simulation_running": self.simulation_running,
            "trains": self.trains,
            "signals": self.signals,
            "platforms": self.platforms,
        }


# Global railway simulation state.
railway_state = RailwayState()
