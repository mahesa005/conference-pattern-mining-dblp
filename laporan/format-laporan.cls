\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{format-laporan}[2026/11/23 Format laporan tugas besar]

% Pass all options to the book class
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax

% Load the base class
\LoadClass[12pt,a4paper]{book}

% --- Main packages ---
\RequirePackage[utf8]{inputenc} % for UTF-8 encoding
\RequirePackage{fontspec} % for font selection
\RequirePackage[indonesian]{babel} % untuk bahasa Indonesia
\RequirePackage{csquotes} % for context-sensitive quotation facilities
\RequirePackage{setspace} % for line spacing
\RequirePackage{graphicx} % for images
\RequirePackage{caption} % for customizing captions
\RequirePackage{subcaption} % for sub-figures
\RequirePackage{tocloft} % for customizing table of contents
\RequirePackage{titlesec} % for customizing titles
\RequirePackage{floatrow} % for customizing float (figure and table) positions
\RequirePackage{listings} % for code listing
\RequirePackage{amsmath} % for math
\RequirePackage{amssymb} % for math symbols
\RequirePackage[shortlabels]{enumitem} % for customizing lists
\RequirePackage[skip=12pt]{parskip} % for spacing between paragraphs
\RequirePackage{longtable} % for long tables
\RequirePackage{booktabs} % for better table rules
\RequirePackage[bahasai]{datetime2} % for date formatting in Indonesian
\RequirePackage{geometry} % for page margins
\RequirePackage{algorithm} % for algorithms
\RequirePackage{algorithmicx} % for algorithmic environment
\RequirePackage{algpseudocode} % for pseudocode
\RequirePackage{microtype} % Untuk optimasi typography dan spacing
\RequirePackage{array} % for better arrays
\RequirePackage{threeparttable} % for tables with notes
\RequirePackage{tabularx} % for tables with adjustable-width columns
\RequirePackage{xcolor} % for color definitions
\RequirePackage[title,titletoc]{appendix} % for appendix management
\RequirePackage{etoolbox}
\RequirePackage{pdfpages}
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,backgrounds,calc}
\tikzset{
  kotak/.style={draw=black!70,rounded corners=1pt,font=\scriptsize,minimum height=0.7cm,text width=3.6cm,align=center,inner sep=2pt},
  sorot/.style={kotak,fill=blue!15,draw=blue!60!black},
  putus/.style={kotak,dashed},
  garis/.style={-{Stealth[length=1.6mm]},black!70},
}
\RequirePackage[hidelinks]{hyperref} % for hyperlinks

\setmainfont{Times New Roman} % set main font to Times New Roman
\onehalfspacing % spasi 1.5

% --- Bibliography menggunakan BibLaTeX, gaya author-date (mendekati CMS) ---
% Template KP dan FAQ meminta Chicago Manual of Style. Paket biblatex-chicago tidak
% terpasang pada instalasi TeX Live basic, jadi dipakai style=authoryear bawaan biblatex.
\RequirePackage[
    style=authoryear,
    backend=biber,
    language=english,
    maxcitenames=2,
    mincitenames=1,
    maxbibnames=10,
    minbibnames=7,
    uniquename=false,
    uniquelist=false,
    dashed=false,
    doi=false,
    isbn=false,
    urldate=long
]{biblatex}
\DeclareLanguageMapping{indonesian}{american}
\DeclareLanguageMapping{bahasa}{american}
\DeclareLanguageMapping{bahasai}{american}
\DeclareLanguageMapping{indon}{american}
\DeclareLabeldate{\field{date}\field{eventdate}\field{origdate}\literal{nodate}}
\urlstyle{same}
\DefineBibliographyExtras{american}{\protected\def\mkbibdatelong#1#2#3{\iffieldundef{#3}{}{\stripzeros{\thefield{#3}}\isdot\iffieldundef{#2}{}{\addspace}}\iffieldundef{#2}{}{\mkbibmonth{\thefield{#2}}\iffieldundef{#1}{}{\addspace}}\iffieldundef{#1}{}{\thefield{#1}}}}
\DefineBibliographyExtras{english}{\protected\def\mkbibdatelong#1#2#3{\iffieldundef{#3}{}{\stripzeros{\thefield{#3}}\isdot\iffieldundef{#2}{}{\addspace}}\iffieldundef{#2}{}{\mkbibmonth{\thefield{#2}}\iffieldundef{#1}{}{\addspace}}\iffieldundef{#1}{}{\thefield{#1}}}}


% --- Bentuk daftar pustaka mendekati CMS: "Penulis. Tahun. Judul." (tanpa tahun dalam kurung) ---
\DeclareDelimFormat[bib,biblist]{nameyeardelim}{\addperiod\space}
\renewbibmacro*{date+extradate}{%
  \iffieldundef{labelyear}
    {}
    {\printtext{\printlabeldateextra}}}
\DeclareFieldFormat[book]{title}{\mkbibemph{#1}}
\DeclareFieldFormat{edition}{\ifinteger{#1}{Edisi ke-#1}{#1\isdot}}

% --- Terjemahan istilah daftar pustaka ke Bahasa Indonesia ---
\DefineBibliographyStrings{english}{
  nodate       = {t.t.},
  and          = {dan},
  andothers    = {dkk.},
  editor       = {penyunting},
  editors      = {penyunting},
  translator   = {penerjemah},
  byeditor     = {disunting oleh},
  bytranslator = {diterjemahkan oleh},
  in           = {dalam},
  edition      = {edisi},
  pages        = {hal.},
  page         = {hal.},
  volume       = {vol.},
  volumes      = {vol.},
  number       = {no.},
  urlseen      = {diakses pada}
}
\DefineBibliographyStrings{american}{
  nodate       = {t.t.},
  and          = {dan},
  andothers    = {dkk.},
  editor       = {penyunting},
  editors      = {penyunting},
  translator   = {penerjemah},
  byeditor     = {disunting oleh},
  bytranslator = {diterjemahkan oleh},
  in           = {dalam},
  edition      = {edisi},
  pages        = {hal.},
  page         = {hal.},
  volume       = {vol.},
  volumes      = {vol.},
  number       = {no.},
  urlseen      = {diakses pada}
}

% --- format sitasi (Penulis Tahun) ---
\let\oldcite\cite
\renewcommand{\cite}{\parencite}

% --- hilangkan koma sebelum 'dan' pada daftar pustaka ---
\renewcommand*{\finalandcomma}{} 

% --- hyperlinks setup ---
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=black
}

% -- No Header dan No Footer ---
\pagestyle{plain}

% --- Ubah nama list of listing ke "DAFTAR LISTING" ---
\renewcommand{\lstlistlistingname}{DAFTAR \textit{LISTING}} 
\renewcommand{\lstlistingname}{\textit{Listing}}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true}

% --- Ubah nama list of algorithm ke "DAFTAR ALGORITMA" ---
\renewcommand{\algorithmname}{Algoritma}
\renewcommand{\listalgorithmname}{DAFTAR ALGORITMA}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true}
\renewcommand{\thealgorithm}{\thechapter.\arabic{algorithm}}

% Create list of equations
\newlistof{myequations}{equ}{DAFTAR PERSAMAAN}
\setlength{\cftmyequationsnumwidth}{3em}
\renewcommand{\cftmyequationsaftersnum}{\hspace{0.5em}}

% Equation caption command (must be used inside numbered line)
\newcommand{\eqcaption}[1]{%
  \addcontentsline{equ}{myequations}
  {\protect\numberline{\theequation}#1}
}
\makeatletter
\renewcommand{\listofmyequations}{%
  \chapter*{\centering\large\bfseries DAFTAR PERSAMAAN}
  \@starttoc{equ}
}
\makeatother

\renewcommand \cftchapdotsep{4.5} % Atur jarak titik-titik pada daftar isi

% -- Atur indentasi judul bab, subbab, dan subsubbab di daftar isi ---
\setlength{\cftchapindent}{0em}
\setlength{\cftchapnumwidth}{4.4em}
\setlength{\cftsecindent}{1.6em} 
\setlength{\cftsecnumwidth}{2.8em} 
\setlength{\cftsubsecindent}{4.4em} 
\setlength{\cftsubsecnumwidth}{3.2em} 
\setlength{\cftsubsubsecindent}{7.6em} 
\setlength{\cftsubsubsecnumwidth}{3.2em} 

% --- Ubah nama bulan ke Bahasa Indonesia ---
\renewcommand*{\DTMbahasaimonthname}[1]{%
  \ifcase#1 %
    \or Januari%  
    \or Februari%  
    \or Maret%  
    \or April%  
    \or Mei%  
    \or Juni%  
    \or Juli%  
    \or Agustus%  
    \or September%  
    \or Oktober%  
    \or November%  
    \or Desember%  
  \fi
}

% --- Atur margin halaman untuk single-sided format (satu muka) ---
\geometry{
      a4paper,
      inner=4cm,
      outer=3cm,
      top=3cm,
      bottom=3cm
}

% --- LISTINGS STYLE FOR PYTHON CODE ---
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.97,0.97,0.97}

\lstdefinestyle{pythonstyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=t,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=4,
    language=Python
}
\lstset{style=pythonstyle}

% --- FORMAT TAMPILAN JUDUL BAB, SUBBAB, JUDUL GAMBAR DAN TABEL ---
\setcounter{tocdepth}{4} 
\setcounter{secnumdepth}{4} 

% --- Judul Bab ---
\titleformat{\chapter}[display]
      {\centering\normalfont\large\bfseries} 
      {\MakeUppercase \chaptertitlename\ \thechapter}{0pt}{\large} 
      \renewcommand\thechapter{\Roman{chapter}}
      
% --- Atur spasi sebelum dan sesudah judul bab/chapter ---  
\titlespacing{\chapter}{0pt}{0pt}{5pt}
\titlespacing{\section}{0pt}{6pt}{6pt}
\titlespacing{\subsection}{0pt}{6pt}{6pt}
\titlespacing{\subsubsection}{0pt}{6pt}{6pt}

% --- Judul Subbab dan Subsubbab ---
\titleformat{\section}
	{\normalfont\bfseries}
	{\thesection}{1em}{}
\titleformat{\subsection}
	{\normalfont\bfseries}
	{\thesubsection}{1em}{}
\titleformat{\subsubsection}
	{\normalfont\bfseries}
	{\thesubsubsection}{1em}{}

% --- Gambar ---
\captionsetup[figure]{
  labelsep=space, 
  format=hang
}  
\floatsetup[figure]{
  capposition=bottom
} 

% --- Tabel ---
\captionsetup[table]{
  labelsep=space, 
  format=hang
} 
\floatsetup[table]{
  capposition=top, 
  objectset=raggedright, 
  captionskip=6pt
} 
\captionsetup[table]{justification=raggedright, singlelinecheck=false}

% --- Listing ---
\captionsetup[lstlisting]{
  labelsep=space, 
  format=hang, 
  justification=raggedright, 
  singlelinecheck=false
}
\floatsetup[lstlisting]{
  capposition=top
}

% --- Algoritma ---
\captionsetup[algorithm]{
  labelsep=space, 
  format=hang, 
  justification=raggedright, 
  singlelinecheck=false
}
\floatsetup[algorithm]{
  capposition=top
}

% --- Atur indentasi paragraf ---
\setlength{\parindent}{0pt}
\setlength{\parskip}{12pt plus 2pt minus 1pt}

\setlist[enumerate]{nosep, topsep=-10pt} 
\setlist[itemize]{nosep, topsep=-10pt} 

\renewcommand{\cftchappresnum}{BAB~}
\settowidth{\cftchapnumwidth}{BAB~12\quad}

% ============================================================
% Tambahan khusus laporan KP
% ============================================================

% --- Daftar lampiran ---
\newlistof{lampiran}{lamp}{DAFTAR LAMPIRAN}
\setlength{\cftlampirannumwidth}{3em}
\makeatletter
\renewcommand{\listoflampiran}{%
  \chapter*{\centering\large\bfseries DAFTAR LAMPIRAN}
  \@starttoc{lamp}
}
\makeatother
\newcommand{\lampirancaption}[1]{\addcontentsline{lamp}{lampiran}{\protect\numberline{\thechapter}#1}}

% --- Placeholder gambar (diganti includegraphics saat gambar tersedia) ---
\newcommand{\gambarplaceholder}[2][5cm]{%
  \fbox{\parbox[c][#1][c]{0.86\textwidth}{\centering\itshape [Placeholder gambar]\\[4pt]\upshape #2}}}

% --- Penanda pemakaian pertama singkatan (untuk Daftar Singkatan) ---
% Pakai \pertama{kunci} tepat di kata pertama kali singkatan itu muncul.
\newcommand{\pertama}[1]{\phantomsection\label{sg:#1}}
\newcommand{\halsg}[1]{\pageref{sg:#1}}

% --- Garis tanda tangan dan tanggal kosong ---
\newcommand{\tanggalkosong}{\makebox[4cm]{\dotfill}}

\endinput