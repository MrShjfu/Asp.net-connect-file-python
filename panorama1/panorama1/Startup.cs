using Microsoft.Owin;
using Owin;

[assembly: OwinStartupAttribute(typeof(panorama1.Startup))]
namespace panorama1
{
    public partial class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            ConfigureAuth(app);
        }
    }
}
