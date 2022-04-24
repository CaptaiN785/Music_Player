import time
from pygame import mixer # To play music
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import *
import threading
import mutagen # To extract image from audio file

app = QApplication(sys.argv)

class Player(QMainWindow):
    def __init__(self, Parent = None):
        super().__init__()
        self.setFixedSize(400, 430)
        self.setWindowTitle("Music player")
        self.setWindowIcon(QIcon("images/music.png"))
        self.show()

        mixer.init()
        
        # Helping variables
        self.musicList = []
        self.running = False
        self.songStarted = False
        self.playingIndex = 0
        self.volume = 1
        self.volume = float(self.volume)
        self.thrd = None
        self.musicPosition = 0


        # Firstly asking for selecting music if not loaded previously
        with open("musicList.txt", "r") as file:
            files = file.readlines()
            for name in files:
                self.musicList.append(name.strip())

            if(len(self.musicList) == 0 or self.musicList[0] == '\n'):
                self.loadMusic()
            else:
                mixer.music.load(self.musicList[0])
                self.playingIndex = 0
                
        ###################

        self.gui = QWidget(self)
        self.layout = QVBoxLayout()
        self.gui.setLayout(self.layout)
        self.gui.setContentsMargins(20, 0, 20, 20)

        self.musicIcon = QPixmap("images/music.png")
        self.musicIconLabel = QLabel()
        self.musicIconLabel.setPixmap(self.musicIcon.scaled(160, 160,transformMode=Qt.TransformationMode.SmoothTransformation))
        self.musicIconLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.musicIconLabel.setStyleSheet("""
            max-width:160px;
            max-height:160px;
            padding:20px;
            margin:0;
            margin-left:60px;
            """)
        self.musicIconLabel.setMinimumSize(250, 210)
        self.layout.addWidget(self.musicIconLabel)
        
        self.musicName = QLabel("---------------------------------------------")
        self.musicName.setStyleSheet("""
            padding:5px 10px;
            background:'#68ebf2';
            color:'#00f';
            font-size:16px;
            max-height:26px;
            margin-top:30px;
        """)
        self.layout.addWidget(self.musicName)
        self.setCentralWidget(self.gui)
        self.gui.setStyleSheet("background:'#9efaff';")
        

        self.hl = QHBoxLayout() # Horixontal layout for all button of functions
        self.hl.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.hl)

        # volume down button
        self.minus = QPushButton(QIcon("images/minus.png"), "", None)
        self.minus.setIconSize(QSize(40, 40))
        self.minus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minus.clicked.connect(lambda: self.updateVolume(-0.1))
        self.hl.addWidget(self.minus)

        # Music selecting button
        self.selectMusic = QPushButton(QIcon("images/selectMusic.png"), "", None)
        self.selectMusic.setIconSize(QSize(40, 40))
        self.selectMusic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.selectMusic.clicked.connect(self.loadMusic)
        self.hl.addWidget(self.selectMusic)

        # play previuos song
        self.prev = QPushButton(QIcon("images/prev.png"),"", None)
        self.prev.setIconSize(QSize(40, 40))
        self.prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev.clicked.connect(self.prevSong)
        self.hl.addWidget(self.prev)

        self.mainBtn = QPushButton()
        self.mainBtn.setIcon(QIcon("images/play.png"))
        self.mainBtn.setIconSize(QSize(60, 60))
        self.mainBtn.setFixedSize(60, 60)
        self.mainBtn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mainBtn.clicked.connect(self.playSong)
        self.hl.addWidget(self.mainBtn)
        self.mainBtn.setStyleSheet("""border-radius:30px;""")

        self.next = QPushButton(QIcon("images/next.png"),"", None)
        self.next.setIconSize(QSize(40, 40))
        self.next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next.clicked.connect(self.nextSong)
        self.hl.addWidget(self.next)

        self.stop = QPushButton(QIcon("images/stop.png"),"", None)
        self.stop.setIconSize(QSize(40, 40))
        self.stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop.clicked.connect(self.stopMusic)
        self.hl.addWidget(self.stop)

        self.plus = QPushButton(QIcon("images/plus.png"), "", None)
        self.plus.setIconSize(QSize(40, 40))
        self.plus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plus.clicked.connect(lambda: self.updateVolume(0.1))
        self.hl.addWidget(self.plus)

        self.currentTime = QLabel("00:00")
        self.currentTime.setStyleSheet("""font-size:16px;color:'#00f';""")

        self.progressBar = QSlider(Qt.Orientation.Horizontal)
        self.progressBar.setPageStep(2)
        self.progressBar.setRange(0, 30)
        self.progressBar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # self.progressBar.valueChanged.connect(self.skip)

        
        self.timeLabel = QLabel("00:00")
        self.timeLabel.setStyleSheet("""font-size:16px;color:'#00f';""")

        self.progressBarLayout = QHBoxLayout()
        self.progressBarLayout.addWidget(self.currentTime)
        self.progressBarLayout.addStrut(5)
        self.progressBarLayout.addWidget(self.progressBar)
        self.progressBarLayout.addStrut(5)
        self.progressBarLayout.addWidget(self.timeLabel)
        self.layout.addLayout(self.progressBarLayout)


        self.setStyleSheet("""
            QPushButton{
                border-radius:20px;
                max-width:40px;
                max-height:40px;
                margin:auto 0;
            }
            QPushButton:pressed{
                border:1px solid '#000';
            }
            QSlider:hover{
                background:'#f00';
            }
        """)

    def closeEvent(self, QCloseEvent) : # overriding for closing all threads or events
        self.running = False
        return super().closeEvent(QCloseEvent)
    
    def skip(self):
        pass
        # val = self.progressBar.value()
        # self.musicPosition = val
        # if self.running:
        #     pass
        #     # self.stopMusic()
        #     # mixer.music.pause()
        #     # self.running = False
        #     # mixer.music.load(self.musicList[self.playingIndex])
        #     # self.playSong()
        #     # mixer.music.set_pos(int(val))
        

    def playSong(self):
        if(self.running == True and self.songStarted == True):
            mixer.music.pause()
            self.mainBtn.setIcon(QIcon("images/play.png"))
            self.running = False
        elif self.songStarted == True and self.running == False:
            mixer.music.unpause()
            self.mainBtn.setIcon(QIcon("images/pause.png"))
            self.running = True
        else:
            self.setMusicName()
            mixer.music.set_volume(self.volume)
            mixer.music.play()
            mixer.music.set_pos(self.musicPosition)
            self.mainBtn.setIcon(QIcon("images/pause.png"))
            self.songStarted = True
            self.running = True
            sg = mixer.Sound(self.musicList[self.playingIndex])
            tm = sg.get_length()
            self.updateTimeLabel(self.timeLabel, tm)
            self.progressBar.setRange(0, int(tm+1))

        self.thrd = threading.Thread(target=self.updateSlider)
        self.thrd.start()
        print("Thread started")
            
    def stopMusic(self):
        if self.running == True:
            mixer.music.stop()
        self.mainBtn.setIcon(QIcon("images/play.png"))
        self.songStarted = False
        self.running = False
        self.musicPosition = 0
        self.progressBar.setValue(0)
        self.updateTimeLabel(self.currentTime, 0)
    
    def loadMusic(self):
        fileName = QFileDialog.getOpenFileNames(self,
        "Select Musics", "", "Music Files (*.mp3 *.wav)")

        error = ([], '')
        if fileName == error:
            print("No song selected")
            return

        try:
            with open("musicList.txt" , "w") as file:
                self.musicList = []
                for name in fileName[0]:
                    name = name.strip()
                    if name.endswith(".mp3") or name.endswith(".wav"):
                        file.write(name+"\n")
                        self.musicList.append(name)
            
            if self.running == True:
                self.stopMusic()
            mixer.music.load(self.musicList[0])
            self.playingIndex = 0

        except Exception as e:
            print("Error while loading musiscs.")
    
    def nextSong(self):
        self.musicPosition = 0
        noOfsongs = len(self.musicList)
        self.stopMusic()
        checks = True
        while checks:
            try:
                self.playingIndex = (noOfsongs + self.playingIndex+1)%noOfsongs
                mixer.music.load(self.musicList[self.playingIndex])
                self.playSong()
                print("Playing next song")
                checks = False
            except Exception as e:
                print("Error while loading next song.")

    def prevSong(self):
        self.musicPosition = 0
        noOfsongs = len(self.musicList)
        self.stopMusic()
        checks = True
        while checks:
            try:
                self.playingIndex = (noOfsongs + self.playingIndex-1)%noOfsongs
                mixer.music.load(self.musicList[self.playingIndex])
                self.playSong()
                print("Playing previous song")
                checks = False
            except Exception as e:
                print("Error while loadin pervious song.")

    def setMusicName(self):
        temp = self.musicList[self.playingIndex].rfind("/")
        self.musicName.setText(self.musicList[self.playingIndex][temp+1:])
        # adding music image to player
        try:
            pxmp = QPixmap()
            metadata = mutagen.File(self.musicList[self.playingIndex])
            if metadata:
                for tag in metadata.tags.values():
                    if tag.FrameID == 'APIC':
                        pxmp.loadFromData(tag.data)
                        break
                if not pxmp.isNull():
                    self.musicIconLabel.setPixmap(pxmp.scaled(160, 160))
                else:
                    self.musicIconLabel.setPixmap(QPixmap("images/music.png").scaled(160, 160,transformMode=Qt.TransformationMode.SmoothTransformation))
            else:
                self.musicIconLabel.setPixmap(QPixmap("images/music.png").scaled(160, 160,transformMode=Qt.TransformationMode.SmoothTransformation))
        except:
            self.musicIconLabel.setPixmap(QPixmap("images/music.png").scaled(160, 160,transformMode=Qt.TransformationMode.SmoothTransformation))

    def updateVolume(self, amount):
        if amount > 0:
            self.volume = min(1, self.volume + 0.1)
            mixer.music.set_volume(self.volume)
        else:
            self.volume = max(0, self.volume - 0.1)
            mixer.music.set_volume(max(0, self.volume))

    def updateSlider(self):
        while mixer.music.get_busy() and self.running:
            self.updateTimeLabel(self.currentTime, self.musicPosition)
            self.progressBar.setValue(self.musicPosition)
            time.sleep(1)
            self.musicPosition = mixer.music.get_pos()//1000
            # Problems while changing song positions
        if self.running :
            self.nextSong()
        print("Song closed")

    def updateTimeLabel(self, label, time):
        second = int(time)
        minute = second//60
        second = second%60
        label.setText("{}:{}".format(minute, second))

if __name__ == '__main__':
    w = Player()
    sys.exit(app.exec())
