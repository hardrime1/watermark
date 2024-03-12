import os 
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.ExifTags import TAGS
from pathlib import Path



class photo:
    def __init__(self,path):
        self.path = path
        self.name = self.path.name
        self.artstr=str(self.exif_info['Artist'])
        self.mkrstr=str(self.exif_info['Make'])
        self.mdlstr=str(self.exif_info['Model'])
        self.lemstr=str(self.exif_info['LensModel']).strip('\x00')


    @property
    def exif_info(self):
        image = Image.open(self.path)
        exif_data = image._getexif()
        exif_info = {}
        if exif_data==None:
            exif_data={}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif_info[tag_name] = value
        b=['Artist','Make','Model','ExposureTime','FNumber','ISOSpeedRatings','FocalLength','LensModel','Orientation','DatetimeOriginal']
        for a in b:
            if a not in exif_info.keys():
                exif_info[a]='-'
        return exif_info
    
    @property
    def img(self):
        i=self.exif_info['Orientation']
        iminit = Image.open(self.path)
        if i==8:
            im=iminit.transpose(Image.Transpose.ROTATE_90)
        elif i==7:
            imi=iminit.transpose(Image.Transpose.ROTATE_270)
            im=imi.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif i==6:
            im=iminit.transpose(Image.Transpose.ROTATE_270)
        elif i==5:
            imi=iminit.transpose(Image.Transpose.ROTATE_270)
            im=imi.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif i==4:
            im=iminit.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif i==3:
            im=iminit.transpose(Image.Transpose.ROTATE_180)
        elif i==2:
            im=iminit.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            im=iminit
        return im

    @property
    def lens_focal_length(self):
        a=str(self.exif_info['FocalLength'])
        if a!='-':
            focal_length = int(self.exif_info['FocalLength'])
            return str(str(focal_length) + 'mm')
        else:
            return(self.exif_info['FocalLength'])
    
    @property
    def exp_aperture(self):
        a=str(self.exif_info['FNumber'])
        if a!='-':
            fnumber = self.exif_info['FNumber']
            return str('f/' + '%.1f'%(fnumber))
        else:
            return self.exif_info['FNumber']
    
    @property
    def exp_shutterspeed(self):
        a=str(self.exif_info['ExposureTime'])
        if a!='-':
            if eval(a)>1:
                tmp = a
            else:
                tmp="1/"+str(int(eval("1/"+a)))+"s"
            return str(tmp)
        else:
            return a
    
    @property
    def exp_iso(self):
        a=str(self.exif_info['ISOSpeedRatings'])
        if a.isnumeric():
            iso = int(self.exif_info['ISOSpeedRatings'])
            return str('ISO' + str(iso))
        else:
            return self.exif_info['ISOSpeedRatings']
    
    @property
    def dtmstr(self):
        if 'DateTimeOriginal' in self.exif_info:
            dtmstr = self.exif_info['DateTimeOriginal']
            date = dtmstr.split(' ')[0].split(':')
            time = dtmstr.split(' ')[1].split(':')
            return str(date[0] + '-' + date[1] + '-' + date[2] + '  ' +
                    time[0] + ':' + time[1])
    
    @property
    def watermark_info(self):
        # Define the text to be printed
        left_info = [
            f"{self.mkrstr} {self.mdlstr}",
            f"{self.lemstr}"
        ]
        right_info = [
            f"{self.lens_focal_length} {self.exp_aperture} {self.exp_shutterspeed} {self.exp_iso}",
            f"{self.dtmstr}"
        ]
        return left_info, right_info
    
    @property
    def watermark_logo(self):
        branch= self.mkrstr.lower()
        logo_dir = Path('logo/')
        logo_Name = logo_dir/(branch+".jpg")
        logo_all=list(logo_dir.glob('**/*.jpg'))
        if logo_Name in logo_all:
            logo_img = Image.open(logo_Name)
        else:
            logo_img=Image.new("RGB",(200,200),"white")
        return logo_img

    def add_watermark(self):
        img = self.img
        width, height = img.size
        left_text, right_text = self.watermark_info
        logo_img = self.watermark_logo
        
        # calculate border size based on the image size
        border_percentage = 0.03
        border_short = int(min(width, height)*border_percentage)
        border_long = border_short * 4

        # create a new image with a white border
        new_size = (width + 2*border_short, height + border_short + border_long)
        new_img = Image.new("RGB", new_size, "white")
        new_img.paste(img, (border_short, border_short))

        # prepare to draw text on the image
        draw = ImageDraw.Draw(new_img)
        text_height = border_short*0.75
        font_small = ImageFont.truetype('fonts/NotoSansSC-Light.ttf', text_height)
        font_large = ImageFont.truetype('fonts/NotoSansSC-Bold.ttf', text_height)

        # draw text
        left_text_position = (int(border_short*2), 
                              int(height + border_short*2))
        right_text_width = draw.textlength(right_text[0], font=font_large)
        right_text_position = (int(new_size[0] - right_text_width - border_short*2), 
                               int(height + border_short*2))

        line_height = border_short * 1
        for i, line in enumerate(left_text):
            if i == 0:
                draw.text(left_text_position, line, font=font_large, fill="black")
            else:
                draw.text(left_text_position, line, font=font_small, fill="black")
            left_text_position = (left_text_position[0], left_text_position[1] + line_height)
        for i, line in enumerate(right_text):
            if i == 0:
                draw.text(right_text_position, line, font=font_large, fill="black")
            else:
                draw.text(right_text_position, line, font=font_small, fill="black")
            right_text_position = (right_text_position[0], right_text_position[1] + line_height)

        # draw cutting line
        line_start = (int(right_text_position[0] - border_short), 
                      int(right_text_position[1]))
        line_end = (int(right_text_position[0] - border_short), 
                    int(right_text_position[1] - line_height * len(right_text)))
        draw.line([line_start, line_end], fill="black", width=int(border_short*0.05))

        # logo resize
        logo_height = int(border_short * 1)
        logo_width = int((logo_height / logo_img.height) * logo_img.width)
        logo_img = logo_img.resize((logo_width, logo_height))

        # draw logo
        logo_position = (int(right_text_position[0] - logo_width - border_short*2),
                         int(height + border_short * 2.7))
        new_img.paste(logo_img, logo_position)

        new_img.save('output/%s'%(self.name))
    


def process(folder_path):
    li=Path(folder_path)
    Li=list(li.glob('**/*.JPG'))
    for i in range(0,len(Li)):
        a=photo(Li[i])
        a.add_watermark()

if __name__ == '__main__':
    folder_path  =Path('image/')
    process(folder_path)