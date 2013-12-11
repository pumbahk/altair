; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=TSSVG extension for Inkscape
AppVerName=TSSVG extension for Inkscape 0.1
DefaultDirName={code:InkscapeDir|share\extensions}
OutputBaseFilename=tssvg.setup
UsePreviousAppDir=no

; Tell Windows Explorer to reload the environment
ChangesEnvironment=yes

[Files]
;Source:"tssvg_*"; Excludes:"*.pyc"; DestDir: "{code:InkscapeDir|share\extensions}"
;Source:"tssvg\*"; Excludes:"*.pyc"; DestDir: "{code:InkscapeDir|share\extensions\tssvg}" 
Source:"tssvg_*"; Excludes:"*.pyc"; DestDir: "{app}"
Source:"tssvg\*"; Excludes:"*.pyc"; DestDir: "{app}\tssvg" 
Source:"tssvg\tests\*"; Excludes:"*.pyc"; DestDir: "{app}\tssvg\tests" 

[UninstallDelete]
Type:files; Name: "{app}\tssvsvg_*"
Type:filesandordirs; Name: "{app}\tssvg}"	

[Registry]
Root:HKCU; SubKey: "Environment"; ValueType: String; ValueName: "PATH"; ValueData: "{olddata};{code:NewBinPath}"; Check: NotOnPathAlready(); Flags: preservestringtype

[Code]
//debug
procedure DisplayPath(prefix :String);
var
   Path	:  String;
begin
   (*
   if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'PATH', Path) then
   begin
      MsgBox(prefix+' : '+Path, mbInformation, MB_OK);
   end
   *)
end;


function InkscapeDir(suffix :String ): String;
var
  installedPath: String;
begin
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Classes\Applications\Inkscape.exe\shell\Inkscape\Command', '', installedPath) then
  begin
    // installedPath = '"foo/bar/inkscape.exe" "%1"'
    Result := Copy(installedPath, 2, pos('Inkscape.exe', installedPath)-1-pos('"', installedPath)-1);
    if(Length(suffix) > 0) then
    begin
       Result := Result + '\' + suffix;
    end
    // MsgBox(Result, mbInformation, MB_OK);
end
  else
  begin
   Result := '';
  end
end;

function InkscapeInstalled(): Boolean;
var
  installedPath: String;
begin
  installedPath := InkscapeDir('');
  //Log('Could not access HKCU\Environment\PATH so assume it is ok to add it');
  result := Length(installedPath) > 0
end;

function RemoveFromString(removed : String; target : String): String;
var
   FoundIndex :Integer;
begin 
   FoundIndex := Pos(removed, target);
   if(FoundIndex = 0) then
   begin
      Result := target;
   end
   else
   begin
      Result := Copy(target, 1, FoundIndex-1) + Copy(target, FoundIndex+Length(removed)+1, Length(target));
   end
end;

function NotOnPathAlready(): Boolean;
var
   Path,InkscapePath: String;
begin
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'PATH', Path) then
  begin
     InkscapePath := InkscapeDir('');
     Result := Pos(InkscapePath, Path) = 0;
     if Result then
     begin
	DisplayPath('check. (not on path)');
	Log('not on path, so add it: ' + InkscapePath);
	Result := True;
     end
  end
  else
  begin
     Result := True;
  end
end;

function NewBinPath(DUMMY :String ): String;
begin
   Result := InkscapeDir('')+';'+InkscapeDir('python')+';';
end;

(*
-----------------
 Event Functions
------------------ 
*)
function InitializeSetup(): Boolean;
begin
   Result := InkscapeInstalled();
   DisplayPath('initialize');
   if(Result = False)then
   begin
      MsgBox('inkscape is not found. abort.', mbInformation, MB_OK);      
   end
end;

procedure DeinitializeUninstall();
var
   Path	: String;
begin
   //MsgBox('inkscape maintenance path', mbInformation, MB_OK);      
   Log('maintenance: PATH\n');
   DisplayPath('uninstall before');
   if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'PATH', Path) then
   begin
      Path := RemoveFromString(';'+NewBinPath(''), Path);
      if not RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'PATH', Path) then
      begin
	 Log('PATH overwrite failured. why?');
      end
   end;
   DisplayPath('uninstall after');
end;

procedure DeinitializeSetup();
begin
   DisplayPath('deinitialize');
end;

[Languages]
Name: japanese; MessagesFile: compiler:Languages\Japanese.isl 

