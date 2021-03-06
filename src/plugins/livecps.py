from plugins.pyseco_plugin import pyseco_plugin


class livecps(pyseco_plugin):
    # str: manialink id
    # float: pos x
    # float: pos y
    # float: pos z
    # float: background w
    # float: background h
    # str: style
    # str: substyle
    # float: label x
    # float: label y
    # float: label z
    # float: label w
    # float: label h
    # float: textsize
    # str: label text
    manialink_str = """<manialink id='%s'>
        <frame posn='%f %f %f' halign='left' valign='top'>
            <quad sizen='%f %f' style='%s' substyle='%s'/>
            <label posn='%f %f %f' sizen='%f %f' textsize='%f' text='%s'/>
            <label posn='%f %f %f' sizen='%f %f' textsize='%f' text='%s'/>
        </frame>
    </manialink>"""

    def __init__(self, pyseco):
        pyseco_plugin.__init__(self, pyseco)
        self.initialize()
        self.register_callback("TrackMania.PlayerCheckpoint")
        self.register_callback("TrackMania.BeginRace")
        self.register_callback("TrackMania.PlayerConnect")
        self.register_callback("TrackMania.EndRound")

    def initialize(self):
        value = self.pyseco.query((), "GetCurrentMapInfo")
        self.new_map(value[0])
        self.ingame = True

    def process_callback(self, value):
        if value[1] == "TrackMania.PlayerCheckpoint":
            self.process_checkpoint(value[0])
        elif value[1] == "TrackMania.BeginRace":
            self.new_map(value[0])
            self.ingame = True
        elif value[1] == "TrackMania.PlayerConnect":
            if self.ingame:
                self.new_player(value[0][0])
        elif value[1] == "TrackMania.EndRound":
            self.ingame = False

    def new_player(self, login):
        for cp, val in self.checkpoint_recs.items():
            if cp == self.nb_checkpoints - 1:
                continue
            self.update_checkpoint_manialink(cp, val["time"],
                self.pyseco.get_player(val["player"]).get_nick_name(),
                login=login)

    def process_checkpoint(self, value):
        player = value[1]
        time = value[2]
        cp = value[4]
        # Dont show the finish time
        if cp == self.nb_checkpoints - 1:
            return
        if (cp not in self.checkpoint_recs) or (time < self.checkpoint_recs[cp]["time"]):
            self.checkpoint_recs[cp] = {"player": player, "time": time}
            self.update_checkpoint_manialink(
                cp, time, self.pyseco.get_player(player).get_nick_name())

    def update_checkpoint_manialink(self, num_cp, time, name, login=None):
        row = int(num_cp / 6)
        column = num_cp % 6
        id_ = "livecps%d" % num_cp
        self.pyseco.add_manialink(id_, ingame=True)
        xml = self.manialink_str % (id_, -48.5 + column*16, 45 - row*4, 0, 15, 3, "BgsPlayerCard", "BgCard", 0.75, -0.75, 0, 10.5, 1.5, 1.5, "$fffCP%d: %s" % (num_cp+1, name.replace("'","&apos;")), 11.5, -0.75, 0, 2.75, 1.5, 1.5, "$0$fff| %d.%03d" % (int(time/1000), time % 1000))
        if login is None:
            self.pyseco.query((xml, 0, False), "SendDisplayManialinkPage")
        else:
            self.pyseco.query((login, xml, 0, False), "SendDisplayManialinkPageToLogin")

    def new_map(self, value):
        self.nb_checkpoints = value[0]["NbCheckpoints"]
        self.checkpoint_recs = dict()
