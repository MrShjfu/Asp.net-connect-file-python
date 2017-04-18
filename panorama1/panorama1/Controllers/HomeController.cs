using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Web;
using System.Web.Mvc;

namespace Panorama.Controllers
{
    public class HomeController : Controller
    {
        public ActionResult Index()
        {
            return View();
        }
        [HttpPost]
        public ActionResult UploadImages(IEnumerable<HttpPostedFileBase> files)
        {
            var uploadedFiles = new List<string>();
            var prefix = Guid.NewGuid().ToString();
            foreach (var file in files)
            {
                var uploadedFilename = Path.Combine(Path.GetTempPath(), $"{prefix}_{file.FileName}");
                uploadedFiles.Add(uploadedFilename);
                file.SaveAs(uploadedFilename);
            }

            var output = RunPythonApp(uploadedFiles);
            Console.WriteLine(output);
            ViewBag.imagesResult = output;
            return View();
        }

        private string RunPythonApp(IEnumerable<string> uploadedFiles)
        {
            // pythonFile địa chỉ file chứa file stitching.py
            var pythonFile = @"D:/me/PanoramaUwithGui/stitching.py";
            var parameters = $"{string.Join(" ", uploadedFiles.Select(s => "\"" + s + "\""))}";
            var fullParameters = "\""+HttpContext.Server.MapPath("~").Replace(@"\\",@"\")+@"Content\"+"image.jpg\"" + @" " + parameters;
            var command = $"{pythonFile} {fullParameters}";
            var start = new ProcessStartInfo
            {
                // FileName địa chỉ file chứa file python.exe (Python2.7)
                FileName = @"C:/Python27/python.exe",
                Arguments = command,
                UseShellExecute = false,
                RedirectStandardOutput = true
            };
            using (var process = Process.Start(start))
            {
                using (var reader = process.StandardOutput)
                {
                    var result = reader.ReadToEnd();
                    return result.Replace("\r\n","");
                }
            }
        }
    }
}