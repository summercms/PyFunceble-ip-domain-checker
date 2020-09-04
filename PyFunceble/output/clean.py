"""
The tool to check the availability or syntax of domain, IP or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provides the cleaning interface.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/special-thanks.html

Contributors:
    https://pyfunceble.github.io/contributors.html

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io/en/dev/

Project homepage:
    https://pyfunceble.github.io/

License:
::


    Copyright 2017, 2018, 2019, 2020 Nissar Chababy

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from os import sep as directory_separator
from os import walk

import PyFunceble
from PyFunceble.engine.database.loader import session
from PyFunceble.engine.database.schemas import File, Status


class Clean:
    """
    Provide the cleaning logic.

    .. note::
        By cleaning we mean the cleaning of the :code:`output` directory.

    :param list_to_test: The list of domains we are testing.
    :type list_to_test: list|None

    :param bool clean_all:
        Tell the subsystem if we need to clean all.
        Which include, of course, the output directory but also
        all other file(s) generated by our system.
    :param str file_path:
        The path to the file we tested.

        .. note::
            This is only relevant if you use the MariaDB/MySQL database.
    """

    def __init__(self, clean_all=False, file_path=None):
        # We clean the output directory.
        self.almost_everything(clean_all, file_path)

    @classmethod
    def file_to_delete(cls, all_files=False):
        """
        Return the list of file to delete.
        """

        # We initiate the directory we have to look for.
        directory = "{0}{1}".format(
            PyFunceble.OUTPUT_DIRECTORY, PyFunceble.OUTPUTS.parent_directory
        )

        if not directory.endswith(directory_separator):  # pragma: no cover
            # For safety, if it does not ends with the directory separator, we append it
            # to its end.
            directory += directory_separator

        # We initiate a variable which will save the list of file to delete.
        result = []

        for root, _, files in walk(directory):
            # We walk in the directory and get all files and sub-directories.

            for file in files:
                # If there is files in the current sub-directory, we loop
                # through the list of files.

                if file in [".gitignore", ".keep"]:
                    continue

                if (
                    not all_files and "logs" in root and ".log" in file
                ):  # pragma: no cover
                    continue

                # The file is not into our list of file we do not have to delete.

                if root.endswith(directory_separator):
                    # The root ends with the directory separator.

                    # We construct the path and append the full path to the result.
                    result.append(root + file)
                else:
                    # The root directory does not ends with the directory separator.

                    # We construct the path by appending the directory separator
                    # between the root and the filename and append the full path to
                    # the result.
                    result.append(root + directory_separator + file)  # pragma: no cover

        # We return our list of file to delete.
        return result

    @classmethod
    def databases_to_delete(cls):  # pragma: no cover
        """
        Set the databases files to delete.
        """

        # We initate the result variable.
        result = []

        # We initiate the directory we have to look for.
        directory = PyFunceble.CONFIG_DIRECTORY

        # We append the dir_structure file.
        result.append(
            "{0}{1}".format(directory, PyFunceble.OUTPUTS.default_files.dir_structure)
        )

        # We append the iana file.
        result.append("{0}{1}".format(directory, PyFunceble.OUTPUTS.default_files.iana))

        # We append the public suffix file.
        result.append(
            "{0}{1}".format(directory, PyFunceble.OUTPUTS.default_files.public_suffix)
        )

        # We append the inactive database file.
        result.append(
            "{0}{1}".format(directory, PyFunceble.OUTPUTS.default_files.inactive_db)
        )

        # We append the mining database file.
        result.append(
            "{0}{1}".format(directory, PyFunceble.OUTPUTS.default_files.mining)
        )

        # We append the hashes tracker file.
        result.append(
            "{0}{1}".format(
                directory, PyFunceble.abstracts.Infrastructure.HASHES_FILENAME
            )
        )

        # We append the user agent file.
        result.append(
            "{0}{1}".format(
                directory, PyFunceble.abstracts.Infrastructure.USER_AGENT_FILENAME
            )
        )

        # We append our downtime file.
        result.append(
            "{0}{1}".format(
                directory, PyFunceble.abstracts.Infrastructure.DOWN_FILENAME
            )
        )

        # We append the ipv4 reputation file.
        result.append(
            "{0}{1}".format(
                directory, PyFunceble.abstracts.Infrastructure.IPV4_REPUTATION_FILENAME,
            )
        )

        return result

    def almost_everything(self, clean_all=False, file_path=False):
        """
        Delete almost all discovered files.

        :param bool clean_all:
            Tell the subsystem if we have to clean everything instesd
            of almost everything.
        """

        if (
            "do_not_clean" not in PyFunceble.INTERN
            or not PyFunceble.INTERN["do_not_clean"]
        ):
            # We get the list of file to delete.
            to_delete = self.file_to_delete(clean_all)

            if (
                not PyFunceble.abstracts.Version.is_local_cloned() and clean_all
            ):  # pragma: no cover
                to_delete.extend(self.databases_to_delete())

            for file in to_delete:
                # We loop through the list of file to delete.

                # And we delete the currently read file.
                PyFunceble.helpers.File(file).delete()

                PyFunceble.LOGGER.info(f"Deleted: {file}")

            if PyFunceble.CONFIGURATION.db_type in [
                "mariadb",
                "mysql",
            ]:  # pragma: no cover

                if file_path:

                    with session.Session() as db_session:
                        # pylint: disable=no-member, singleton-comparison
                        to_delete = (
                            db_session.query(Status)
                            .join(File)
                            .filter(File.path == file_path)
                            .filter(File.test_completed == True)
                            .filter(
                                Status.status.in_(PyFunceble.core.CLI.get_up_statuses())
                            )
                            .all()
                        )

                    for row in to_delete:
                        with session.Session() as db_session:
                            # pylint: disable=no-member, singleton-comparison
                            delete_query = Status.__table__.delete().where(
                                Status.id == row.id
                            )
                            db_session.execute(delete_query)
                            db_session.commit()

                    with session.Session() as db_session:
                        # pylint: disable=no-member, singleton-comparison
                        file_object = (
                            db_session.query(File).filter(File.path == file_path).one()
                        )

                    file_object.test_completed = False

                    with session.Session() as db_session:
                        # pylint: disable=no-member, singleton-comparison
                        db_session.add(file_object)
                        db_session.commit()
                else:
                    with session.Session() as db_session:
                        # pylint: disable=no-member, singleton-comparison
                        to_delete = db_session.query(  # pylint: disable=no-member
                            File
                        ).all()

                    for row in to_delete:
                        # pylint: disable=no-member
                        with session.Session() as db_session:
                            # pylint: disable=no-member, singleton-comparison

                            delete_query = File.__table__.delete().where(
                                File.id == row.id
                            )
                            db_session.execute(delete_query)
                            db_session.commit()

            if (
                not PyFunceble.abstracts.Version.is_local_cloned() and clean_all
            ):  # pragma: no cover
                PyFunceble.load_config()

                PyFunceble.LOGGER.info("Reloaded configuration.")
